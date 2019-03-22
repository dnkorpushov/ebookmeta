from lxml import etree
from lxml.etree import QName

import base64

from .metadata import Metadata
from .utils import xstr, person_sort_name
from .myzipfile import ZipFile, is_zipfile


class Fb2Meta:

    ns = {
        'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0',
        'l': 'http://www.w3.org/1999/xlink'
    }

    def __init__(self, file):

        self.file = file
        self.tree = None
        self.encoding = ''

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
        meta.title = xstr(self.get('//fb:description/fb:title-info/fb:book-title/text()'))
        meta.author = self.get_author_list()
        meta.author_sort = []
        for author in meta.author:
            meta.author_sort.append(person_sort_name(author))

        meta.series = self.get_series()
        meta.series_index = self.get_series_index()
        meta.tag = self.get_genre_list()
        meta.translator = self.get_translator_list()
        meta.lang = xstr(self.get('//fb:description/fb:title-info/fb:lang/text()'))
        meta.src_lang = xstr(self.get('//fb:description/fb:title-info/fb:src-lang/text()'))
        meta.date = xstr(self.get('//fb:description/fb:title-info/fb:date/text()'))
        meta.publisher = xstr(self.get('//fb:description/fb:publish-info/fb:publisher/text()'))
        meta.description = self.get_description()
        meta.cover_image_data = self.get_cover_data(self.get_cover_name())
        meta.identifier = xstr(self.get('//fb:description/fb:document-info/fb:id/text()'))
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
        for node in node_list:
            author = self.get_person(node)
            author_list.append(author)
        return author_list

    def get_translator_list(self):

        node_list = self.getall('//fb:description/fb:title-info/fb:translator')
        translator_list = []
        for node in node_list:
            translator = self.get_person(node)
            translator_list.append(translator)
        return translator_list

    def get_person(self, node):

        first_name = ''
        middle_name = ''
        last_name = ''

        for e in node:
            if QName(e).localname == 'first-name':
                first_name = xstr(e.text)
            elif QName(e).localname == 'middle-name':
                middle_name = xstr(e.text)
            elif QName(e).localname == 'last-name':
                last_name = xstr(e.text)

        author = '{} {} {}'.format(first_name, middle_name, last_name)
        return ' '.join(author.split())

    def get_genre_list(self):

        genre_list = []
        node_list = self.getall('//fb:description/fb:title-info/fb:genre')
        for n in node_list:
            genre_list.append(n.text)
        return genre_list

    def get_series(self):

        return xstr(self.get('//fb:description/fb:title-info/fb:sequence/@name'))

    def get_series_index(self):

        index = ''
        index = xstr(self.get('//fb:description/fb:title-info/fb:sequence/@number'))
        return index

    def get(self, xpath):

        result_list = self.tree.xpath(xpath, namespaces=self.ns)
        for n in result_list:
            return n

    def getall(self, xpath):

        return self.tree.xpath(xpath, namespaces=self.ns)

    def set_metadata(self, metadata):

        # Generate new title-info for fb2
        title_info = etree.Element('title-info', nsmap=self.ns)
        etree.SubElement(title_info, 'book-title', nsmap=self.ns).text = metadata.title

        for author in metadata.author:
            node = self.create_person_node('author', author)
            title_info.append(node)

        for tag in metadata.tag:
            etree.SubElement(title_info, 'genre', nsmap=self.ns).text = tag

        if metadata.series:
            series_node = etree.SubElement(title_info, 'sequence', nsmap=self.ns)
            series_node.attrib['name'] = metadata.series
            if metadata.series_index:
                series_node.attrib['number'] = str(metadata.series_index)

        if metadata.description:
            node = etree.SubElement(title_info, 'annotation', nsmap=self.ns)
            etree.SubElement(node, 'p', nsmap=self.ns).text = metadata.description

        if metadata.date:
            etree.SubElement(title_info, 'date', nsmap=self.ns).text = metadata.date

        if metadata.lang:
            etree.SubElement(title_info, 'lang', nsmap=self.ns).text = metadata.lang

        if metadata.src_lang:
            etree.SubElement(title_info, 'src-lang', nsmap=self.ns).text = metadata.src_lang

        for translator in metadata.translator:
            node = self._create_person_node('translator', translator)
            title_info.append(node)

        if metadata.cover_image_data:
            cover_name = self.get_cover_name()
            if cover_name is None:
                cover_name = 'cover.jpg'

            node = etree.SubElement(title_info, 'coverpage', nsmap=self.ns)
            image_node = etree.SubElement(node, 'image', nsmap=self.ns)
            image_node.attrib[QName('http://www.w3.org/1999/xlink', 'href')] = '#{}'.format(cover_name)

            node = self.get('//fb:binary[@id="{0}"]'.format(cover_name))
            if node is None:
                node = etree.SubElement(self.tree.getroot(), 'binary', nsmap=self.ns)
            node.attrib['id'] = cover_name
            node.attrib['content-type'] = 'image/jpeg'
            node.text = base64.encodebytes(metadata.cover_image_data)
        else:
            # Cover cleared - delete cover image if exist
            cover_name = self.get_cover_name()
            if cover_name is not None:
                node = self.get('//fb:binary[@id="{0}"]'.format(cover_name))
                if node is not None:
                    node.getparent().remove(node)

        # replace original title-info
        title_node = self.get('//fb:description/fb:title-info')
        title_node.getparent().replace(title_node, title_info)

        self.save()

    def create_person_node(self, node_name, person):

        first_name = ''
        middle_name = ''
        last_name = ''

        person_parts = person.split()
        if len(person_parts) == 3:
            first_name = person_parts[0]
            middle_name = person_parts[1]
            last_name = person_parts[2]
        elif len(person_parts) == 2:
            first_name = person_parts[0]
            last_name = person_parts[1]
        else:
            last_name = person

        node = etree.Element(node_name, nsmap=self.ns)
        if first_name:
            etree.SubElement(node, 'first-name', nsmap=self.ns).text = first_name.strip()
        if middle_name:
            etree.SubElement(node, 'middle-name', nsmap=self.ns).text = middle_name.strip()
        if last_name:
            etree.SubElement(node, 'last-name', nsmap=self.ns).text = last_name.strip()

        return node
