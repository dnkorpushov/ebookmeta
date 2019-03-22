from .metadata import Metadata
from .exceptions import BadFormat, UnknownFormatException
from .fb2 import Fb2Meta
from .epub2 import Epub2
from .epub3 import Epub3

__all__ = ['get_metadata', 'set_metadata', 'Metadata']


def _get_ebook(file):

    ebook = None
    if file.lower().endswith(('.fb2', '.zip')):
        ebook = Fb2Meta(file)
    elif file.lower().endswith('.epub'):
        try:
            ebook = Epub2(file)
        except BadFormat:
            try:
                ebook = Epub3(file)
            except BadFormat:
                raise UnknownFormatException
    else:
        raise UnknownFormatException

    return ebook


def get_metadata(file):

    ebook = _get_ebook(file)
    metadata = ebook.get_metadata()

    return metadata


def set_metadata(file, metadata):

    ebook = _get_ebook(file)
    ebook.set_metadata(metadata)
