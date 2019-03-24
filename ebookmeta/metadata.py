from lxml import etree

from .fb2genres import fb2genres
from .exceptions import BadLanguage


class Metadata:

    def __init__(self):
        self.id = None
        self.identifier = ''
        self.title = ''
        self.author = []
        self.author_sort = []
        self.translator = []
        self.series = ''
        self.series_index = ''
        self.tag = []
        self.description = ''
        self.lang = ''
        self.src_lang = ''
        self.format = ''
        self.date = ''
        self.publisher = ''
        self.cover_image_data = None
        self.file = ''

    def get_author_string(self):
        if self.author:
            return ', '.join(self.author)
        return ''

    def get_author_sort_string(self):
        if self.author_sort:
            return ', '.join(self.author_sort)
        return ''

    def get_translator_string(self):
        if self.translator is not None:
            return ', '.join(self.translator)
        return ''

    def get_tag_string(self):
        if self.tag:
            return ', '.join(self.tag)

    def get_tag_description_string(self, lang='ru'):

        if lang not in ('ru', 'en'):
            raise BadLanguage('Only ru and en languages supports')
        tag_description = []
        tree = etree.fromstring(fb2genres, parser=etree.XMLParser())
        xpath_str = '//fbgenrestransfer/genre/subgenres/subgenre[@value="{}"]/genre-descr[@lang="{}"]/@title'
        for tag in self.tag:
            node = tree.xpath(xpath_str.format(tag, lang))
            try:
                tag_description.append(str(node[0]))
            except IndexError:
                tag_description.append(tag)
        return ', '.join(tag_description)

    def set_author_from_string(self, author_string):
        self.author = []
        if author_string and len(author_string) > 0:
            for author in author_string.split(','):
                self.author.append(author.strip())

    def set_translator_from_string(self, translator_string):
        self.translator = []
        if translator_string and len(translator_string) > 0:
            for translator in translator_string.split(','):
                self.translator.append(translator.strip())

    def set_tag_from_string(self, tag_string):
        self.tag = []
        if tag_string and len(tag_string) > 0:
            for tag in tag_string.split(','):
                self.tag.append(tag.strip())
