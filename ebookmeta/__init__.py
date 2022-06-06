import os
import re
from unittest import result
from .metadata import Metadata
from .exceptions import BadFormat, UnknownFormatException
from .fb2 import Fb2Meta
from .epub2 import Epub2
from .epub3 import Epub3
from .utils import replace_keywords, splitext_, normalize_path

__all__ = ['get_metadata', 'set_metadata', 'Metadata', 'get_filename_from_pattern']


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



def get_authors_from_pattern(authors, pattern, short=True, lang='ru'):
    if len(authors) == 0:
        return ''

    if short and len(authors) > 1:
        if lang == 'ru':
            return replace_keywords(pattern, _get_person_dict(authors[0])) + ' и др'
        else:
            return replace_keywords(pattern, _get_person_dict(authors[0])) + ', et al'
    else:
        result = []
        for author in authors:
            result.append(replace_keywords(pattern, _get_person_dict(author)))
        return ', '.join(result)


def get_filename_from_pattern(meta, filename_format, author_format, padnum=2):
    d = { 
        '#title': '',
        '#series': '',
        '#abbrseries': '',
        '#ABBRseries': '',
        '#number': '',
        '#padnumber': '',
        '#author': '',
        '#authors': '',
        '#translator': '',
        '#bookid': ''
    }

    d['#title'] = meta.title
    d['#author'] = get_authors_from_pattern(meta.author, author_format, short=True, lang=meta.lang)
    d['#authors'] = get_authors_from_pattern(meta.author, author_format, short=False, lang=meta.lang)
    d['#bookid'] = meta.identifier

    if meta.series:
        d['#series'] = meta.series
        abbr = ''.join(w[0] for w in meta.series.split())
        d['#abbrseries'] = abbr.lower()
        d['#ABBRseries'] = abbr.upper()

    if meta.series_index:
        d['#number'] = str(meta.series_index)
        d['#padnumber'] = str(meta.series_index).strip().zfill(padnum)

    if len(meta.translator) > 0:
        try:
            d['#translator'] = meta.translator[0].split()[-1]
        except:
            d['#translator'] = ''


    file_ext = splitext_(meta.file)
    result = replace_keywords(filename_format, d).strip() + file_ext 
 
    return normalize_path(result)


def _get_person_dict(person):
    d = { '#f': '', '#m': '', '#l': '', '#fi': '', '#mi':'' }
 
    person_parts = person.split()
    if len(person_parts) == 3:
        d['#f'] = person_parts[0]
        d['#m'] = person_parts[1]
        d['#l'] = person_parts[2]
    elif len(person_parts) == 2:
        d['#f'] = person_parts[0]
        d['#l'] = person_parts[1]
    else:
        d['#l'] = person

    if len(d['#f']) > 0:
        d['#fi'] = d['#f'][0] + '.'
    if len(d['#m']) > 0: 
        d['#mi']= d['#m'][0] + '.'
    return d

