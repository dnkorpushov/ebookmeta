from lxml import etree

from .fb2genres import fb2genres
from .exceptions import BadLanguage
from .utils import str_to_list, replace_keywords, split_ext, normalize_path


class Metadata:
    def __init__(self):
        self.identifier = None
        self.title = None
        self.author_list = []
        self.author_sort_list = []
        self.translator_list = []
        self.series = None
        self.series_index = None
        self.tag_list = []
        self.description = None
        self.lang = None
        self.format = None
        self.format_version = None
        self.cover_image_data = None
        self.cover_file_name = None
        self.cover_media_type = None
        self.file = None

    def author_list_to_string(self):
        return ', '.join(self.author_list) if self.author_list else []

    def translator_list_to_string(self):
        return ', '.join(self.translator_list) if self.translator_list else []

    def tag_list_to_string(self):
        return ', '.join(self.tag_list) if self.tag_list else []

    def tag_description_list_to_string(self, lang='ru'):
        if lang not in ('ru', 'en'):
            raise BadLanguage('Only ru and en languages supports')
        result = []
        tree = etree.fromstring(fb2genres, parser=etree.XMLParser())
        xpath_str = '//fbgenrestransfer/genre/subgenres/subgenre[@value="{}"]/genre-descr[@lang="{}"]/@title'
        for tag in self.tag_list:
            node = tree.xpath(xpath_str.format(tag, lang))
            try:
                result.append(str(node[0]))
            except IndexError:
                result.append(tag)
        return ', '.join(result)

    def set_author_list_from_string(self, s):
        self.author_list = str_to_list(s)

    def set_translator_list_from_string(self, s):
        self.translator_list = str_to_list(s)

    def set_tag_list_from_string(self, s):
        self.tag_list = str_to_list(s)

    def get_filename_by_pattern(self, filename_pattern, author_pattern, padnum=2):
        d = { '#title': '', '#series': '', '#abbrseries': '',
              '#ABBRseries': '', '#number': '', '#padnumber': '',
              '#author': '', '#authors': '', '#translator': '',
              '#bookid': ''
            }

        d['#title'] = self.title
        d['#author'] = self._get_authors_by_pattern(author_pattern, short=True)
        d['#authors'] = self._get_authors_by_pattern(author_pattern, short=False)
        d['#bookid'] = self.identifier

        if self.series:
            d['#series'] = self.series
            abbr = ''.join(w[0] for w in self.series.split())
            d['#abbrseries'] = abbr.lower()
            d['#ABBRseries'] = abbr.upper()

            if self.series_index:
                d['#number'] = str(self.series_index)
                d['#padnumber'] = str(self.series_index).strip().zfill(padnum)

            if len(self.translator) > 0:
                try:
                    d['#translator'] = self.translator[0].split()[-1]
                except:
                    d['#translator'] = ''


            file_ext = split_ext(self.file)
            result = replace_keywords(filename_pattern, d).strip() + file_ext 
 
        return normalize_path(result)


    def _get_authors_by_pattern(self, pattern, short=True):
        if len(self.authors) == 0:
            return ''

        if short and len(self.author_list) > 1:
            if self.lang == 'ru':
                return replace_keywords(pattern, self._get_person_dict(self.author_list[0])) + ' и др'
            else:
                return replace_keywords(pattern, self._get_person_dict(self.author_list[0])) + ', et al'
        else:
            result = []
            for author in self.author_list:
                result.append(replace_keywords(pattern, self._get_person_dict(author)))
            return ', '.join(result)


    def _get_person_dict(self, person):
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

    def __str__(self):
        result = []
        for key in self.__dict__.keys():
            if key == 'cover_image_data':
                if self.__dict__[key] is not None:
                    result.append('{0}: {1}'.format(key, '<binary_data>')) 
                else:
                    result.append('{0}: {1}'.format(key, 'None')) 
            else:
                result.append('{0}: {1}'.format(key, self.__dict__[key]))

        return '[' + ', '.join(result) + ']'

    
    

