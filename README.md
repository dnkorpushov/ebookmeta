# ebookmeta

Ebookmeta is a Python library for managing EPUB2/EPUB3 and FB2 files metadata.

## Usage

### Reading
```python
import ebookmeta

metadata = ebookmeta.get_metadata('test.epub')  # returning Metadata class
print(metadata.title)
for author in metadata.author:
    print(author)
```

### Writing

```python
import ebookmeta

metadata = ebookmeta.get_metadata('test.epub')

metadata.title = 'New book title'
metadata.set_author_from_string('Isaac Azimov, Arthur Charles Clarke')

ebookmeta.set_metadata('test.epub', metadata)  # Set epub metadata from Metadata class
```

## Metadata class

### Attributes
* id
* identifier
* title
* author
* author_sort
* translator
* series
* series_index
* tag
* description
* lang
* src_lang
* format
* date
* publisher
* cover_image_data
* file

### Methods
* get_author_string
* get_author_sort_string
* get_translator_string
* get_tag_string
* set_author_from_string
* set_translator_from_string
* set_tag_from_string
