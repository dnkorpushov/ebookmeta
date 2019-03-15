from ebookmeta import get_metadata, set_metadata
from pprint import pprint

if __name__ == '__main__':
    meta = get_metadata('c:/work/test/sous-le-vent.epub')
    meta.title = meta.title + ' 1'
    # meta = set_metadata(meta.file, meta)
    # pprint(meta.author)
    print(meta.author)
    print(vars(meta))

