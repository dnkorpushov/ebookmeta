import os
import tempfile
import datetime
import shutil
from lxml import etree
from lxml.etree import QName

from .metadata import Metadata
from .myzipfile import ZipFile, is_zipfile, ZIP_DEFLATED, ZIP_STORED
from .exceptions import BadFormat, WriteEpubException
from .utils import person_sort_name, xstr


class Epub3:

    ns = {
        'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
        'opf': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }

    def __init__(self, file):

        self.file = file
        self.version = ''
        self.tree = None
        self.content_root = ''
        self.opf_file = ''
        self.cover_href = ''
        self.cover_image_data = None

        self.load()

    def load(self):
        if is_zipfile(self.file):
            z = ZipFile(self.file)
            container = z.read('META-INF/container.xml')
            tree = etree.fromstring(container)
            self.opf_file = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=self.ns)[0]
            opf_data = z.read(self.opf_file)
            z.close()
            self.content_root = os.path.split(self.opf_file)[0]
            if self.content_root:
                self.content_root += '/'
            self.tree = etree.fromstring(opf_data)
            v = self.tree.xpath('/opf:package/@version', namespaces=self.ns)[0]
            self.version = v[:1]
            if self.version != '3':
                raise BadFormat('wrong epub3 version')
        else:
            raise BadFormat('wrong zip format')

    def save(self):

        temp_dir = tempfile.mkdtemp(prefix='em')
        dest_file = os.path.join(temp_dir, os.path.split(self.file)[1])
        src_zip = ZipFile(self.file, mode='r')
        dest_zip = ZipFile(dest_file, mode='w')
        try:
            for f in src_zip.infolist():
                if f.filename == self.opf_file:
                    dest_zip.writestr(self.opf_file, etree.tostring(self.tree, encoding='utf-8',
                                      method='xml', xml_declaration=True, pretty_print=True))

                elif f.filename == self.cover_href:
                    if self.cover_image_data is not None:
                        dest_zip.writestr(self.content_root + self.cover_href, self.cover_image_data)
                elif f.filename == 'mimetype':
                    buf = src_zip.read(f)
                    dest_zip.writestr(f.filename, buf, ZIP_STORED)
                else:
                    buf = src_zip.read(f)
                    dest_zip.writestr(f.filename, buf, ZIP_DEFLATED)
            src_zip.close()
            dest_zip.close()
            shutil.copyfile(dest_file, self.file)
            shutil.rmtree(temp_dir)
        except Exception:
            shutil.rmtree(temp_dir)
            raise WriteEpubException

    def get_metadata(self):

        metadata = Metadata()

        metadata.identifier = {}
        metadata.identifier['value'] = ''
        metadata.identifier['attrib'] = {}
        identifier = self.get('opf:metadata/dc:identifier')
        if identifier is not None:
            metadata.identifier['value'] = identifier.text
            for attr in identifier.attrib:
                metadata.identifier['attrib'][attr] = identifier.attrib[attr]

        title_list = self.getall('opf:metadata/dc:title')
        for e in title_list:
            value = self.get_element_refines(self.get_element_id(e), property='title-type')
            if value == 'main' or not value:
                metadata.title = e.text
        creator_list = self.getall('opf:metadata/dc:creator')
        for e in creator_list:
            value = self.get_element_refines(self.get_element_id(e), property='role')
            if value == 'aut' or not value:
                metadata.author.append(e.text)
                metadata.author_sort.append(person_sort_name(e.text))
            elif value == 'trl':
                metadata.translator.append(e.text)
        metadata.series = xstr(self.get('opf:metadata/opf:meta[@name="calibre:series"]/@content'))
        metadata.series_index = xstr(self.get('opf:metadata/opf:meta[@name="calibre:series_index"]/@content'))
        node_list = self.getall('opf:metadata/dc:subject')
        metadata.tag = []
        for n in node_list:
            metadata.tag.append(n.text)
        metadata.description = xstr(self.get('opf:metadata/dc:description/text()'))
        metadata.lang = xstr(self.get('opf:metadata/dc:language/text()'))
        metadata.date = xstr(self.get('opf:metadata/dc:date/text()'))
        metadata.publisher = xstr(self.get('opf:metadata/dc:publisher/text()'))
        metadata.cover_image_data = self.get_cover_image()
        metadata.format = 'epub'
        metadata.file = self.file

        return metadata

    def get_element_refines(self, id, property):

        value = self.get('opf:metadata/opf:meta[@refines="#{}" and @property="{}"]/text()'.format(id, property))
        if value is not None:
            return xstr(value)
        return ''

    def get_element_id(self, elem):

        return elem.attrib['id'] if 'id' in elem.attrib else ''

    def get_cover_image(self):

        cover_data = None
        cover_href = self.get_cover_href(self.get_cover_id())
        if cover_href is not None:
            z = ZipFile(self.file)
            cover_data = z.read(self.content_root + cover_href)
            z.close()

        return cover_data

    def get_cover_id(self):

        cover_id = self.get('opf:metadata/opf:meta[@name="cover"]/@content')
        if cover_id is None:
            cover_id = self.get('opf:manifest/opf:item[@properties="cover-image"]/@id')
        return cover_id

    def get_cover_href(self, cover_id):

        return self.get('opf:manifest/opf:item[@id="{}"]/@href'.format(cover_id))

    def set_metadata(self, metadata):

        meta = self.Element('opf:metadata')

        if metadata.identifier['value']:
            node = self.SubElement(meta, 'dc:identifier')
            node.text = metadata.identifier['value']
            for attr in metadata.identifier['attrib']:
                node.attrib[attr] = metadata.identifier['attrib'][attr]

        if metadata.title:
            node = self.SubElement(meta, 'dc:title')
            node.text = metadata.title
            node.attrib['id'] = 'title'
            self.add_refines(meta, id='title', property='title-type', text='main')

        idx = 1
        for author in metadata.author:
            self.add_creator(meta, name=author, id='author{}'.format(idx), role='aut')
            idx += 1

        idx = 1
        for translator in metadata.translator:
            self.add_creator(meta, name=translator, id='translator{}'.format(idx), role='trl')
            idx += 1

        for tag in metadata.tag:
            self.SubElement(meta, 'dc:subject').text = tag

        if metadata.description:
            self.SubElement(meta, 'dc:description').text = metadata.description

        if metadata.publisher:
            self.SubElement(meta, 'dc:publisher').text = metadata.publisher

        if metadata.date:
            self.SubElement(meta, 'dc:date').text = metadata.date

        if metadata.lang:
            self.SubElement(meta, 'dc:language').text = metadata.lang

        if metadata.series:
            node = self.SubElement(meta, 'opf:meta')
            node.attrib['name'] = 'calibre:series'
            node.attrib['content'] = metadata.series

        if metadata.series_index:
            node = self.SubElement(meta, 'opf:meta')
            node.attrib['name'] = 'calibre:series_index'
            node.attrib['content'] = str(metadata.series_index)

        node = self.SubElement(meta, 'opf:meta')
        node.attrib['property'] = 'dcterms:modified'
        node.text = datetime.datetime.now().isoformat(timespec='seconds') + 'Z'

        if metadata.cover_image_data is not None:
            cover_id = self.get_cover_id()
            if cover_id is None:
                cover_id = 'coverimage'
            self.cover_href = self.get_cover_href(cover_id)

            node = self.SubElement(meta, 'opf:meta')
            node.attrib['name'] = 'cover'
            node.attrib['content'] = cover_id

            if self.cover_href is None:
                self.cover_href = 'cover.jpg'
            else:
                cover_name, _ = os.path.splitext(self.cover_href)
                self.cover_href = cover_name + '.jpg'

            node = self.get('opf:manifest/opf:item[@id="{}"]'.format(cover_id))
            if node is None:
                node = self.Element('opf:item')
                node.attrib['id'] = cover_id
                manifest_node = self.get('opf:manifest')
                manifest_node.append(node)
            node.attrib['href'] = self.cover_href
            node.attrib['properties'] = 'cover-image'
            node.attrib['media-type'] = 'image/jpeg'
            self.cover_image_data = metadata.cover_image_data

            meta_node = self.get('opf:metadata')
            meta_node.getparent().replace(meta_node, meta)
            self.save()

    def add_creator(self, parent, name, id, role):

        node = self.SubElement(parent, 'dc:creator')
        node.text = name
        node.attrib['id'] = id
        self.add_refines(parent, id=id, property='file-as', text=person_sort_name(name, first_delimiter=', '))
        self.add_refines(parent, id, 'role', role)

    def add_refines(self, parent, id, property, text):

        node = self.SubElement(parent, 'opf:meta')
        node.attrib['refines'] = '#{}'.format(id)
        node.attrib['property'] = property
        node.text = text

    def Element(self, name):

        ns, tag = name.split(':')
        return etree.Element(QName(self.ns[ns], tag), nsmap=self.ns)

    def SubElement(self, parent, name):

        ns, tag = name.split(':')
        return etree.SubElement(parent, QName(self.ns[ns], tag))

    def get(self, name):

        result_list = self.tree.xpath(name, namespaces=self.ns)
        for r in result_list:
            return r

    def getall(self, name):

        return self.tree.xpath(name, namespaces=self.ns)
