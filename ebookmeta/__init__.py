from .metadata import Metadata
from .fb2 import Fb2Meta
from .epub2 import Epub2
from .epub3 import Epub3

__all__ = ['get_metadata', 'set_metadata', 'Metadata']


def get_metadata(file):
    fb2 = Epub3(file)
    metadata = fb2.get_metadata()
    return metadata


def set_metadata(file, metadata):
    fb2 = Epub2(file)
    fb2.set_metadata(metadata)
