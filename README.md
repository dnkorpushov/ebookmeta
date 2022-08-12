# ebookmeta

Ebookmeta is a Python library for managing epub2, epub3 and fb2 files metadata.

Library allows you to read and write some of the metadata fields of epub2, epub3 and fb2 files.

The following fields can be read: identifier, title, authors, tags, book series and series index, language, description, translators, and cover data (image as byte array, file name, and media type).
It is possible to write all fields, excluding description and identifier.

When changing the cover, the library does not check whether the image byte array matches the media type. You must ensure that this data is correct.

There is a limitation for epub files: you can't add cover if it doesn't exist in file. You can only replace an existing cover.

This library used in my other project [Libro2](https://github.com/dnkorpushov/libro2) - GUI tool for editing metadata, rename and convert to other formats for ebook files.

## Installation
### Using pip
```pip3 install ebookmeta```
### From source
```python3 setup.py install```
### Requirements
* lxml

## Usage

### Reading
```python
import ebookmeta

meta = ebookmeta.get_metadata('test.epub')  # returning Metadata class
print(meta.title)
for author in metadata.authors:
    print(author)
```

### Writing
```python
import ebookmeta

meta = ebookmeta.get_metadata('test.epub')
meta.title = 'New book title'
meta.set_author_list(['Isaac Azimov, Arthur Charles Clarke'])

ebookmeta.set_metadata('test.epub', meta)  # Set epub metadata from Metadata class
```

## Metadata class

### Attributes
* identifier - book unique identifier
* title - book title
* author_list - list of book authors
* series - book series title
* series_index - book series index
* tags - book tags
* lang - book language
* description - book description
* translators - book translators (if exists)
* format - file format (epub or fb2)
* format_version - format specification version 
* cover_image_data - cover image byte array
* cover_media_type - cover media type (possible image/jpeg, image/png)
* cover_file_name - stored file name
* file - source file name
* file_created - file creation time in ISO datetime format
* file_modified - file modification time in ISO datetime format

#### Additional attributes for fb2 
* publish_info.title - published book title
* publish_info.publisher - original book bublisher
* publish_info.city - city where original book was published
* publish_info.year - year of publication book
* publish_info.isbn - International Standard Book Number (ISBN)
* publish_info.series - original book sereis
* publish_info.seires_index - original book series index

### Methods 
* author_list_to_string - return authors list as comma-separated string
* translator_list_to_string - return translators list as comma-separated string
* tag_list_to_string - return tag list as comma-separated string
* tag_description_list_to_string - for fb2 return tag description  list as comma-separated string, for epub same tag_list_to_string data
* set_author_list_from_string - sets authors list from comma-separated string
* set_translator_list_from_string - sets translators list from comma-separated string
* set_tag_list_from_string - sets tags list from comma-separated string
* get_filename_by_pattern - returns the file name generated based on the metadata according to the given template


### Metadata.get_filename_by_pattern method
Metadata.**get_filename_by_pattern**(filename_pattern, author_pattern)
Return the filename, based on template.
Template can contain placeholders, path delimiters, and any other characters that are included in the output without modification. 
Usage:
```
meta = ebook.get_metadata('oldfilename.epub')
new_filename = meta.get_filename_by_pattern('#Author. #Title', '#l{ #fi.}')
```
For example, for epub Azimov's Foundation book, return "Azimov I. Foundation.epub" string.

You can group template parts into optional blocks. An optional block is denoted with curly braces {}. An optional block must contain only one placeholder and any number of other characters. The optional block is completely excluded from the result if the value of the placeholder is None. Optional blocks can't be nested.
Usage:
```
meta1 = ebook.get_metadata('book_with_series.epub')
meta2 = ebook.get_metadata('book_without_series.epub')
meta1.get_filename_by_pattern('/books/#Author/{#Series/}{#Number. }#Title', '#l{ #fi.}')
meta2.get_filename_by_pattern('/books/#Author/{#Series/}{#Number. }#Title', '#l{ #fi.}')

```
For example, for epub Azimov's Foundation book if metadata contains series and series_index (Foundation 1), return "/books/Azimov I/Foundation/1. Foundation.epub".
For epub Azimov,s I, robot return "/books/Azimov I/I, robot.epub".

Possible filename placeholders:
- #Title - book title
- #Author - Book author name generated by author pattern. If the book contains more than one author, the "et al" is added at the end of the line. For russian language is "и др".
- #Authors - comma separated list of all book authors. Each author name generated by author pattern. Be careful, if book contain long list of authors.
- #Series - book series title
- #Abbrseries - abbriviated series title. E.g. for "Very long series title" #abbrseries is "Vlst".
- #Number - book series index
- #Padnumber padding left book series index
- #Translator - last name of first book translator
- #Atranslator - book translator name, generate by #Author rules
= #Atranslators - comma separated list of all book tranlsators by #Authors rules
- #Bookid - book unique identifier
- #Md5 - md5 checksum for source file 

Уou can change the letter case of the placeholder value, just put the placeholder name in the right case.
For example:
- #Title - get book title as is
- #TITLE - get book title in UPPER CASE
- #title - get book title in lower case

Possible author name placeholders:
- #f - author first name. Для русского языка - имя автора.
- #m - author middle name. Для русского языка - отчество автора.
- #l - author last name. Для русского языка - фамилия автора.
- #fi - first name initial. Для русского языка - инициал имени.
- #mi - middle name initial. Для русского языка - инициал отчества.
