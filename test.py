from ebookmeta import get_metadata, set_metadata
from pprint import pprint

if __name__ == '__main__':
    for book in ['c:/work/test/sous-le-vent.epub', 'c:/work/4/test.fb2', 'c:/work/test/test.epub']:
        metadata = get_metadata(book)
        print(vars(metadata))

