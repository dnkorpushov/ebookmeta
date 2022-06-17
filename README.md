# ebookmeta

Ebookmeta is a Python library for managing epub2, epub3 andfb2 files metadata

Library allows you to read and write some of the metadata fields of epub2, epub3 and fb2 files.

The following fields can be read: identifier, title, authors, tags, book series and series index, language, description, translators, and cover data (image as byte array, file name, and media type).
It is possible to write all fields, excluding description and identifier.

When changing the cover, the library does not check whether the image byte array matches the media type. You must ensure that this data is correct.

There is a limitation for epub files: you can't add cover if it doesn't exist in file. You can only replace an existing cover.

P.S. 
Sorry for my English


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
* series - book series
* series_index - book series index
* tags - book tags
* lang - book language
* description - book description
* translators - book translators (if exsists)
* format - file format (epub or fb2)
* format_version - format specification version 
* cover_image_data - cover image byte array
* cover_media_type - cover media type (possible image/jpeg, image/png)
* cover_file_name - stored file name
* file - source file name

### Methods 
* author_list_to_string - return authors list as comma-separated string
* translator_list_to_string - return translators list as comma-separated string
* tag_list_to_string - return tag list as comma-separated string
* tag_description_list_to_string - for fb2 return tag description  list as comma-separated string, for epub same tag_list_to_string data
* set_author_list_from_string - sets autors list from comma-separated string
* set_translator_list_from_string - sets translators list from comma-separated string
* set_tag_list_from_string - sets tags list from comma-separated string
* get_filename_by_pattern - returns the file name generated based on the metadata according to the given template


### Get filename by pattern
    Metadata class has get_filename_by_pattern method for generate new filename by pattern based on source file metadata.

## Installation
### Using pip
```pip3 install ebookmeta```
### From source
```python3 setup.py install```
### Requirements
* lxml


