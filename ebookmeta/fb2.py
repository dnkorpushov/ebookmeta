from lxml import etree
from lxml.etree import QName

import base64

from .metadata import Metadata
from .myzipfile import ZipFile, is_zipfile


class Fb2Meta:

    file = ''
    tree = None
    encoding = ''

    def __init__(self, file):

        self.ns = {
                    'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0',
                    'l': 'http://www.w3.org/1999/xlink'
                  }
        self.file = file
        self.load()

    def load(self):

        if is_zipfile(self.file):
            z = ZipFile(self.file)
            fb2_string = z.read(z.infolist()[0])
            self.tree = etree.fromstring(fb2_string)
            z.close()
        else:
            self.tree = etree.parse(self.file, parser=etree.XMLParser(recover=True))
        self.encoding = self.tree.docinfo.encoding

    def save(self):

        if is_zipfile(self.file):
            z = ZipFile(self.file, mode='w')
            z.writestr(z.infolist()[0],
                       etree.tostring(self.tree, encoding=self.encoding,
                                      method='xml', xml_declaration=True, pretty_print=True))
            z.close()
        else:
            self.tree.write(self.file, encoding=self.encoding, method='xml', xml_declaration=True, pretty_print=True)

    def get_metadata(self):

        meta = Metadata()
        meta.title = self.get('//fb:description/fb:title-info/fb:title/text()')
        meta.author = self.get_author_list()
        meta.series = self.get_series()
        meta.series_index = self.get_series_index()
        meta.tag = self.get_genre_list()
        meta.translator = self.get_translator_list()
        meta.lang = self.get('//fb:description/fb:title-info/fb:lang/text()')
        meta.src_lang = self.get('//fb:description/fb:title-info/fb:src-lang/text()')
        meta.date = self.get('//fb:description/fb:title-info/fb:date/text()')
        meta.publisher = self.get('//fb:description/fb:publish-info/fb:publisher/text()')
        meta.description = self.get_description()
        meta.cover_image_data = self.get_cover_data(self.get_cover_name())
        meta.format = 'fb2'
        meta.file = self.file
        return meta

    def get_cover_name(self):

        cover_name = self.get('//fb:description/fb:title-info/fb:coverpage/fb:image/@l:href')
        if cover_name is not None:
            return cover_name[1:]

        return ''

    def get_cover_data(self, name):

        if name:
            node = self.get('//fb:binary[@id="{0}"]'.format(name))
            if node is not None and node.text is not None:
                return base64.b64decode(node.text.encode('ascii'))
        return None

    def get_description(self):

        annotation = self.get('//fb:description/fb:title-info/fb:annotation')
        if annotation is not None:
            return ''.join(annotation.itertext())
        return ''

    def get_author_list(self):

        node_list = self.getall('//fb:description/fb:title-info/fb:author')
        author_list = []
        author_sort_list = []
        for node in node_list:
            author, author_sort = self.get_person(node)
            author_list.append(author)
            author_sort_list.append(author_sort)
        return author_list, author_sort_list

    def get_translator_list(self):

        node_list = self.getall('//fb:description/fb:title-info/fb:translator')
        translator_list = []
        for node in node_list:
            translator, _ = self.get_person(node)
            translator_list.append(translator)
        return translator_list

    def get_person(self, node):

        first_name = ''
        middle_name = ''
        last_name = ''

        for e in node:
            if QName(e).localname == 'first-name':
                first_name = e.text
            elif QName(e).localname == 'middle-name':
                middle_name = e.text
            elif QName(e).localname == 'last-name':
                last_name = e.text

        author = '{} {} {}'.format(first_name, middle_name, last_name)
        return ' '.join(author.split())

    def get_genre_list(self):

        genre_list = []
        node_list = self.getall('//fb:description/fb:title-info/fb:genre')
        for n in node_list:
            genre_list.append(n.text)
        return genre_list

    def get_series(self):

        return self.get('//fb:description/fb:title-info/fb:sequence/@name')

    def get_series_index(self):

        index = ''
        index = self.get('//fb:description/fb:title-info/fb:sequence/@number')
        return index

    def get(self, xpath):

        result_list = self.tree.xpath(xpath, namespaces=self.ns)
        for n in result_list:
            return n

    def getall(self, xpath):

        return self.tree.xpath(xpath, namespaces=self.ns)

    def set_metadata(self, meta):
        # Generate new title-info for fb2
        nsmap = {None: 'http://www.gribuser.ru/xml/fictionbook/2.0', 'l': 'http://www.w3.org/1999/xlink'}
        title_info = etree.Element('title-info', nsmap=nsmap)
        etree.SubElement(title_info, 'book-title').text = meta.title
        for author in meta.author:
            node = self._create_person_node('author', author)
            title_info.append(node)
        for tag in meta.tag:
            etree.SubElement(title_info, 'genre').text = tag
        if meta.series:
            series_node = etree.SubElement(title_info, 'sequence')
            series_node.attrib['name'] = meta.series
            if meta.series_index:
                series_node.attrib['number'] = str(meta.series_index)
        if meta.description:
            node = etree.SubElement(title_info, 'annotation')
            etree.SubElement(node, 'p').text = meta.description
        if meta.date:
            etree.SubElement(title_info, 'date').text = meta.date
        if meta.cover_image_name:
            node = etree.SubElement(title_info, 'coverpage')
            image_node = etree.SubElement(node, 'image')
            image_node.attrib[QName('http://www.w3.org/1999/xlink', 'href')] = '#{}'.format(meta.cover_image_name)
        else:
            # Cover cleared - delete cover image if exist
            cover_name, cover_data = self._get_cover()
            if cover_name and cover_data is not None:
                node = self._find('//fb:binary[@id="{0}"]'.format(cover_name))
                if node is not None:
                    node.getparent().remove(node)
        if meta.lang:
            etree.SubElement(title_info, 'lang').text = meta.lang
        if meta.src_lang:
            etree.SubElement(title_info, 'src-lang').text = meta.src_lang
        for translator in meta.translator:
            node = self._create_person_node('translator', translator)
            title_info.append(node)

        # replace original title-info
        title_node = self._find('//fb:description/fb:title-info')
        title_node.getparent().replace(title_node, title_info)

        # Change cover image
        if meta.cover_image_name and meta.cover_image_data is not None:
            node = self._find('//fb:binary[@id="{0}"]'.format(meta.cover_image_name))
            if node is None:
                node = etree.SubElement(self.tree.getroot(), 'binary')
            node.attrib['id'] = meta.cover_image_name
            node.attrib['content-type'] = 'image/jpeg'
            node.text = base64.encodebytes(meta.cover_image_data)

    def _create_person_node(self, node_name, person):
        node = etree.Element(node_name)
        if person.first_name:
            etree.SubElement(node, 'first-name').text = person.first_name
        if person.middle_name:
            etree.SubElement(node, 'middle-name').text = person.middle_name
        if person.last_name:
            etree.SubElement(node, 'last-name').text = person.last_name

        return node
