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

### Methods
