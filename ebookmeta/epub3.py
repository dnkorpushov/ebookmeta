
from .epub2 import Epub2
from .utils import xstr

class Epub3(Epub2):
    ####### Getters (override) #######
    def get_title(self):
        node = self._get_title_node()
        if node is not None:
            return xstr(node.text)
            
    def get_author_list(self):
        result = []
        node_list = self._get_person_node_list('aut')
        for node in node_list: result.append(xstr(node.text))
        return result

    def get_translator_list(self):
        result = []
        node_list = self._get_person_node_list('trl')
        for node in node_list: result.append(xstr(node.text))
        return result

    def get_cover_data(self):
        media_type = None
        href = None
        data = None
        node = self._get('opf:manifest/opf:item[@properties="cover-image"]')
        if node is not None:
            if 'media-type' in node.attrib: media_type = node.attrib['media-type']
            if 'href'in node.attrib: href = node.attrib['href']
            if href: data = self._get_file_content(self.content_root + href)
        return (href, media_type, data)

    ####### Setters (override) #######
    def set_title(self, title):
        node = self._get_title_node()
        if node is not None:
            node.text = title

    def set_author_list(self, author_list):
        self._set_person_list(author_list, 'aut')

    def set_translator_list(self, translator_list):
        self._set_person_list(translator_list, 'trl')

    def set_cover_data(self, href, media_type, data):
        (href, _, _) = self.get_cover_data()
        if href and data:
            self.cover_href = href
            self.cover_data = data

    ####### Service methods #######
    def _set_person_list(self, person_list, role):
        node_list = self._get_person_node_list(role)
        for node in node_list:
            if 'id' in node.attrib:
                refine_list = self._get_all('opf:metadata/opf:meta[@refines="#{0}"]'.format(node.attrib['id']))
                for refine in refine_list: refine.getparent().remove(refine)
            node.getparent().remove(node)

        meta_node = self._get('opf:metadata')
        index = 1 
        for person in person_list:
            node = self._sub_element(meta_node, 'dc:creator')
            node.text = person
            node.attrib['id'] = '{0}{1:02d}'.format(role, index)
            node.tail = '\n'
            refine = self._sub_element(meta_node, 'opf:meta')
            refine.attrib['refines'] = '#{0}{1:02d}'.format(role, index)
            refine.attrib['scheme']='marc:relators'
            refine.attrib['property'] = 'role'
            refine.text = role
            refine.tail = '\n'

            index += 1

    def _get_title_node(self):
        node_list = self._get_all('opf:metadata/dc:title')
        for node in node_list:
            refines_list = self._get_all('opf:metadata/opf:meta[@refines="#{0}" and @property="title-type"]'.format(self._get_element_id(node)))
            if len(refines_list) == 0:
                return node
            else:
                for refines in refines_list:
                    if refines.text == 'main':
                        return node
    
    def _get_person_node_list(self, role):
        result_list = []
        node_list = self._get_all('opf:metadata/dc:creator')
        for node in node_list:
            refines_list = self._get_all('opf:metadata/opf:meta[@refines="#{0}" and @property="role"]'.format(self._get_element_id(node)))
            if len(refines_list) == 0 and role == 'aut':
                result_list.append(node)
            else:
                for refines in refines_list:
                    if refines.text == role:
                        result_list.append(node)
                        break

        return result_list

    def _get_element_refines(self, id, property):
        value = self._get('opf:metadata/opf:meta[@refines="#{0}" and @property="{1}"]'.format(id, property))
        if value is not None:
            return xstr(value.text)
        return ''

    def _get_element_id(self, e):
        return e.attrib['id'] if 'id' in e.attrib else ''