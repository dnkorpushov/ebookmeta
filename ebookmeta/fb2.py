from lxml import etree
import base64
from io import BytesIO

from .utils import xstr
from .myzipfile import ZipFile, is_zipfile

ns_map = {
    'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0',
    'l': 'http://www.w3.org/1999/xlink'
}

class Fb2():
    def __init__(self, file):
        self.file = file
        self.tree = None
        self.encoding = None
        self.zip_file_name = None

        if is_zipfile(self.file):
            zipfile = ZipFile(self.file)
            for info in zipfile.infolist():
                self.zip_file_name = info
            
            if self.zip_file_name:
                content = zipfile.read(self.zip_file_name)
                self.tree = etree.parse(BytesIO(content), parser=etree.XMLParser(recover=True))
                self.encoding = self.tree.docinfo.encoding
                zipfile.close()
        else:
            self.tree = etree.parse(self.file, parser=etree.XMLParser(recover=True))
            self.encoding = self.tree.docinfo.encoding

    ######## Getters ########
    def get_title(self):
        return xstr(self._get('//fb:description/fb:title-info/fb:book-title/text()'))

    def get_author_list(self):
        node_list = self._get_all('//fb:description/fb:title-info/fb:author')
        result_list = []
        for node in node_list:
            person = self._get_person(node)
            result_list.append(person)
        return result_list
    
    def get_series(self):
         return xstr(self._get('//fb:description/fb:title-info/fb:sequence/@name'))

    def get_series_index(self):
        return xstr(self._get('//fb:description/fb:title-info/fb:sequence/@number'))

    def get_lang(self):
        return xstr(self._get('//fb:description/fb:title-info/fb:lang/text()'))
    
    def get_tag_list(self):
        tag_list = []
        node_list = self._get_all('//fb:description/fb:title-info/fb:genre')
        for n in node_list:
            tag_list.append(xstr(n.text))
        return tag_list

    def get_description(self):
        content = self._get('//fb:description/fb:title-info/fb:annotation')
        if content is not None:
            return ''.join(content.itertext())

    def get_translator_list(self):
        node_list = self._get_all('//fb:description/fb:title-info/fb:translator')
        result_list = []
        for node in node_list:
            person = self._get_person(node)
            result_list.append(person)
        return result_list

    def get_format(self):
        return 'fb2'
    
    def get_format_version(self):
        return '2.0'

    def get_identifier(self):
        return xstr(self._get('//fb:description/fb:document-info/fb:id/text()'))

    def get_cover_data(self):
        media_type = None
        href = None
        data = None

        href = self._get('//fb:description/fb:title-info/fb:coverpage/fb:image/@l:href')
        if href:
            href = href[1:] # Crop # symbol
            node = self._get('//fb:binary[@id="{0}"]'.format(href))
            if node is not None:
                if 'content-type' in node.attrib:
                    media_type = node.attrib['content-type']
                    data = base64.b64decode(node.text.encode('ascii'))
        return (href, media_type, data)

    def get_publish_title(self):
        return xstr(self._get('//fb:description/fb:publish-info/fb:book-name/text()'))

    def get_publish_publisher(self):
        return xstr(self._get('//fb:description/fb:publish-info/fb:publisher/text()'))
    
    def get_publish_year(self):
        return xstr(self._get('//fb:description/fb:publish-info/fb:year/text()'))

    def get_publish_city(self):
        return xstr(self._get('//fb:description/fb:publish-info/fb:city/text()'))
    
    def get_publish_isbn(self):
        return xstr(self._get('//fb:description/fb:publish-info/fb:isbn/text()'))

    def get_publish_series(self):
         return xstr(self._get('//fb:description/fb:publish-info/fb:sequence/@name'))

    def get_publish_series_index(self):
        return xstr(self._get('//fb:description/fb:publish-info/fb:sequence/@number'))
    

    ######## Setters ########
    def set_title(self, title):
        node = self._get('//fb:description/fb:title-info/fb:book-title')
        if node is None:
            parent = self._get('//fb:description/fb:title-info')
            node = self._sub_element(parent, 'fb:book-title')
        node.text = title

    def set_author_list(self, author_list):
        node_list = self._get_all('//fb:description/fb:title-info/fb:author')
        for node in node_list: node.getparent().remove(node)
        parent = self._get('//fb:description/fb:title-info')
        for author in author_list:
            node = self._sub_element(parent, 'fb:author')
            self._set_person(node, author)
       
    def set_series(self, series):
        node = self._get('//fb:description/fb:title-info/fb:sequence')
        if series:
            if node is None:
                parent = self._get('//fb:description/fb:title-info')
                node = self._sub_element(parent, 'fb:sequence')
            node.attrib['name'] = series
        else:
            if node is not None:
                node.getparent().remove(node)

    def set_series_index(self, series_index):
        node = self._get('//fb:description/fb:title-info/fb:sequence')
        if series_index:
            if node is None:
                parent = self._get('//fb:description/fb:title-info')
                node = self._sub_element(parent, 'fb:sequence')
            node.attrib['number'] = str(series_index)
        else:
            if node is not None:
                node.getparent().remove(node)

    def set_lang(self, lang):
        node = self._get('//fb:description/fb:title-info/fb:lang')
        if node is None:
            parent = self._get('//fb:description/fb:title-info')
            node = self._sub_element(parent, 'fb:lang')
        node.text = lang

    def set_tag_list(self, tag_list):
        node_list = self._get_all('//fb:description/fb:title-info/fb:genre')
        for node in node_list: node.getparent().remove(node)
        parent = self._get('//fb:description/fb:title-info')
        for tag in tag_list:
            node = self._sub_element(parent, 'fb:genre')
            node.text = tag

    def set_translator_list(self, translator_list):
        node_list = self._get_all('//fb:description/fb:title-info/fb:translator')
        for node in node_list: node.getparent().remove(node)
        parent = self._get('//fb:description/fb:title-info')
        for translator in translator_list:
            node = self._sub_element(parent, 'fb:translator')
            self._set_person(node, translator)

    def set_cover_data(self, href, media_type, data):
        old_href = self._get('//fb:description/fb:title-info/fb:coverpage/fb:image/@l:href')
        if old_href:
            href = old_href[1:] # Crop # symbol
        else:
            parent = self._get('//fb:description/fb:title-info')
            node = self._sub_element(parent, 'fb:coverpage')
            image_node = self._sub_element(node, 'fb:image')
            image_node.attrib[etree.QName('http://www.w3.org/1999/xlink', 'href')] = '#{}'.format(href)

        node = self._get('//fb:binary[@id="{0}"]'.format(href))
        if node is None:
            node = self._sub_element(self.tree.getroot(), 'fb:binary')
            node.attrib['id'] = href
            node.attrib['content-type'] = media_type
        
        node.text = base64.encodebytes(data)

    def set_publish_title(self, title):
        node = self._get('//fb:description/fb:publish-info/fb:book-name')
        if node is None:
            parent = self._get('//fb:description/fb:publish-info')
            node = self._sub_element(parent, 'fb:book-name')
        node.text = title

    def set_publish_publisher(self, publisher):
        node = self._get('//fb:description/fb:publish-info/fb:publisher')
        if node is None:
            parent = self._get('//fb:description/fb:publish-info')
            node = self._sub_element(parent, 'fb:publisher')
        node.text = publisher

    def set_publish_year(self, year):
        node = self._get('//fb:description/fb:publish-info/fb:year')
        if node is None:
            parent = self._get('//fb:description/fb:publish-info')
            node = self._sub_element(parent, 'fb:year')
        node.text = year

    def set_publish_city(self, city):
        node = self._get('//fb:description/fb:publish-info/fb:city')
        if node is None:
            parent = self._get('//fb:description/fb:publish-info')
            node = self._sub_element(parent, 'fb:city')
        node.text = city    

    def set_publish_isbn(self, isbn):
        node = self._get('//fb:description/fb:publish-info/fb:isbn')
        if node is None:
            parent = self._get('//fb:description/fb:publish-info')
            node = self._sub_element(parent, 'fb:isbn')
        node.text = isbn

    def set_publish_series(self, series):
        node = self._get('//fb:description/fb:publish-info/fb:sequence')
        if series:
            if node is None:
                parent = self._get('//fb:description/fb:publish-info')
                node = self._sub_element(parent, 'fb:sequence')
            node.attrib['name'] = series
        else:
            if node is not None:
                node.getparent().remove(node)

    def set_publish_series_index(self, series_index):
        node = self._get('//fb:description/fb:publish-info/fb:sequence')
        if series_index:
            if node is None:
                parent = self._get('//fb:description/fb:publish-info')
                node = self._sub_element(parent, 'fb:sequence')
            node.attrib['number'] = str(series_index)
        else:
            if node is not None:
                node.getparent().remove(node)

    ######## Service methods ########
    def save(self):
        if is_zipfile(self.file):
            zipfile = ZipFile(self.file, mode='w')
            zipfile.writestr(self.zip_file_name,
                       etree.tostring(self.tree, encoding=self.encoding,
                                      method='xml', xml_declaration=True, pretty_print=True))
            zipfile.close()
        else:
            self.tree.write(self.file, encoding=self.encoding, method='xml', 
                            xml_declaration=True, pretty_print=True)

    def _get_person(self, node):
        first_name = ''
        middle_name = ''
        last_name = ''

        for e in node:
            if etree.QName(e).localname == 'first-name':
                first_name = xstr(e.text)
            elif etree.QName(e).localname == 'middle-name':
                middle_name = xstr(e.text)
            elif etree.QName(e).localname == 'last-name':
                last_name = xstr(e.text)

        author = '{0} {1} {2}'.format(first_name, middle_name, last_name)
        return ' '.join(author.split())

    def _set_person(self, node, person):

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
    
        if first_name:
            self._sub_element(node, 'fb:first-name').text = first_name.strip()
        if middle_name:
            self._sub_element(node, 'fb:middle-name').text = middle_name.strip()
        if last_name:
            self._sub_element(node, 'fb:last-name').text = last_name.strip()


    def _get(self, xpath):
        node_list = self.tree.xpath(xpath, namespaces=ns_map)
        for node in node_list:
            return node

    def _get_all(self, xpath):
        return self.tree.xpath(xpath, namespaces=ns_map)

    def _sub_element(self, parent, name):
        ns, tag = name.split(':')
        return etree.SubElement(parent, etree.QName(ns_map[ns], tag))
