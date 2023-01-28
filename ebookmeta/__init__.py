from .metadata import Metadata
from .exceptions import BadFormat, UnknownFormatException
from .fb2 import Fb2
from .epub2 import Epub2
from .epub3 import Epub3
from .utils import get_file_creation_time, get_file_modified_time

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
    if file.lower().endswith('.fb2.zip'):
        meta.format = ebook.get_format_if_zip()
    else:
        meta.format = ebook.get_format()
    meta.format_version = ebook.get_format_version()
    meta.file = file
    meta.file_created = get_file_creation_time(file)
    meta.file_modified = get_file_modified_time(file)

    # Get publish info for FB2
    if meta.format == 'fb2':
        meta.publish_info.title = ebook.get_publish_title()
        meta.publish_info.publisher = ebook.get_publish_publisher()
        meta.publish_info.city = ebook.get_publish_city()
        meta.publish_info.year = ebook.get_publish_year()
        meta.publish_info.series = ebook.get_publish_series()
        meta.publish_info.series_index = ebook.get_publish_series_index()
        meta.publish_info.isbn = ebook.get_publish_isbn()
   
    return meta

def set_metadata(file, meta):
    ebook = _get_ebook(file)

    ebook.set_title(meta.title)
    ebook.set_author_list(meta.author_list)
    ebook.set_series(meta.series)
    ebook.set_series_index(meta.series_index)
    ebook.set_lang(meta.lang)
    ebook.set_tag_list(meta.tag_list)
    ebook.set_translator_list(meta.translator_list)
    ebook.set_cover_data(meta.cover_file_name, meta.cover_media_type, meta.cover_image_data)

    # Set publish info for FB2
    if meta.format == 'fb2':
        ebook.set_publish_title(meta.publish_info.title)
        ebook.set_publish_publisher(meta.publish_info.publisher)
        ebook.set_publish_city(meta.publish_info.city) 
        ebook.set_publish_year(meta.publish_info.year)
        ebook.set_publish_series(meta.publish_info.series)
        ebook.set_publish_series_index(meta.publish_info.series_index)
        ebook.set_publish_isbn(meta.publish_info.isbn)
   
    ebook.save()

