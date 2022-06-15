from .metadata import Metadata
from .exceptions import BadFormat, UnknownFormatException
from .fb2 import Fb2
from .epub2 import Epub2
from .epub3 import Epub3

__all__ = ['get_metadata', 'set_metadata', 'Metadata', 'get_filename_from_pattern']


def _get_ebook(file):
    ebook = None
    
    if file.lower().endswith(('.fb2', '.zip')):
        ebook = Fb2(file)

    elif file.lower().endswith('.epub'):
        ebook = Epub2(file)
        if ebook.version[:1] == '3':
            ebook = Epub3(file)
    else:
       raise UnknownFormatException 

    return ebook


def get_metadata(file):
    ebook = _get_ebook(file)
    meta = Metadata()

    meta.identifier = ebook.get_identifier()
    meta.title = ebook.get_title()
    meta.author_list = ebook.get_author_list()
    meta.series = ebook.get_series()
    meta.series_index = ebook.get_series_index()
    meta.lang = ebook.get_lang()
    meta.description = ebook.get_description()
    meta.tag_list = ebook.get_tag_list()
    meta.translator_list = ebook.get_translator_list()
    (meta.cover_file_name, meta.cover_media_type, meta.cover_image_data) = ebook.get_cover_data()
    meta.format = ebook.get_format()
    meta.format_version = ebook.get_format_version()
    meta.file = file
   
    return meta

def set_metadata(file, meta):
    ebook = _get_ebook(file)

    ebook.set_title(meta.title)
    ebook.set_author_list(meta.author_list)
    ebook.set_series(meta.series)
    ebook.set_series_index(meta.series_index)
    ebook.set_lang(meta.lang)
    ebook.set_translator_list(meta.translator_list)
    ebook.set_cover_data(meta.cover_file_name, meta.cover_media_type, meta.cover_image_data)
    ebook.save()



