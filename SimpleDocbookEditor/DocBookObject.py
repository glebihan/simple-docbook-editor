# DocBookObject.py
# -*- coding=utf-8 -*-
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-
#
# Copyright © 2014 Gwendal Le Bihan
# 
# This file is part of Simple DocBook Editor.
# 
# Simple DocBook Editor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Simple DocBook Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Simple DocBook Editor.  If not, see <http://www.gnu.org/licenses/>.

import libxml2
import os
import logging
import urlparse
import hashlib

OBJECT_IDS = 0

EDIT_MODES = {
    "book": "raw",
    "chapter": "html",
    "sect1": "html",
    "sect2": "html",
    "sect3": "html"
}

DOCBOOK_TO_HTML_NODES = {
    "chapter": "div",
    "sect1": "div",
    "sect2": "div",
    "sect3": "div",
    "note": "div",
    "figure": "figure",
    "screenshot": "div",
    "imageobject": "div",
    "mediaobject": "div",
    "title": "h1",
    "para": "p",
    "itemizedlist": "ul",
    "listitem": "li",
    "wordasword": "span",
    "guilabel": "span",
    "replaceable": "span",
    "guibutton": "span",
    "guimenu": "span",
    "guisubmenu": "span",
    "guimenuitem": "span",
    "keycombo": "span",
    "keycap": "span",
    "screen": "div",
    "command": "div",
    "table": "table",
    "thead": "thead",
    "tbody": "tbody",
    "row": "tr",
    "entry": "td",
    "ulink": "a",
    "imagedata": "img"
}
DOCBOOK_ELEMENT_TYPE_TO_CLASS = [
    "chapter",
    "sect1",
    "sect2",
    "sect3",
    "guilabel",
    "note",
    "wordasword",
    "screen",
    "command",
    "replaceable",
    "guibutton",
    "guimenu",
    "guisubmenu",
    "guimenuitem",
    "keycombo",
    "keycap",
    "screenshot",
    "mediaobject",
    "imageobject",
]
DOCBOOK_JUMP_NODES = [
    "tgroup"
]
DOCBOOK_TO_HTML_PROPS = {
    "url": "href",
    "fileref": "src",
    "id": "id",
    "width": "width"
}
HTML_TO_DOCBOOK_NODES = {
    "p": "para",
    "h1": "title",
    "ul": "itemizedlist",
    "li": "listitem",
    "table": "table",
    "thead": "thead",
    "tbody": "tbody",
    "tr": "row",
    "td": "entry",
    "a": "ulink",
    "figure": "figure",
    "figcaption": "title",
    "img": "imagedata"
}
HTML_JUMP_NODES = [
    "body",
    "html"
]
HTML_TO_DOCBOOK_PROPS = {
    "id": "id",
    "href": "url",
    "width": "width",
    "src": "fileref"
}

libxml2.registerErrorHandler(lambda f, ctx: None, None)

class DocBookObject(object):
    def __init__(self, parent = None, **params):
        global OBJECT_IDS
        
        self._parent = parent
        self._params = params
        
        self._saved_state = None
        
        self._already_warned_unconverted_docbook_node_type = []
        self._already_warned_unconverted_html_node_type = []
        self._already_warned_unconverted_docbook_prop = []
        self._already_warned_unconverted_html_prop = []
        
        OBJECT_IDS += 1
        self.object_id = OBJECT_IDS
        
        self._children = []
        
        assert ("filename" in self._params) or ("xml_object" in self._params)
        
        if "filename" in params and params["filename"] != None:
            self._load_from_file()
        else:
            self._load_from_xml_object(params["xml_object"])
    
    def _get_filename(self):
        return self._params.setdefault("filename", None)
    filename = property(_get_filename)
    
    def get_real_filename(self):
        if self.filename:
            return self.filename
        else:
            return self._parent.get_real_filename()
    
    def _load_from_file(self):
        logging.debug("Parsing file %s" % self.filename)
        
        self._xml_document = libxml2.parseFile(self.filename)
        self._load_from_xml_object(self._xml_document.getRootElement())
    
    def _load_from_xml_object(self, xml_object):
        self._xml_root = xml_object
        new_children = []
        if xml_object.children:
            child = xml_object.children
            while child:
                if child.name == "include":
                    include_filename = os.path.join(os.path.split(self.filename)[0], child.prop("href"))
                    if os.path.exists(include_filename):
                        new_children.append(DocBookObject(self, filename = include_filename))
                    else:
                        new_children.append(DocBookObject(self, xml_object = child))
                else:
                    already_loaded_child = self.find_by_node(child)
                    if already_loaded_child:
                        new_children.append(already_loaded_child)
                    else:
                        new_children.append(DocBookObject(self, xml_object = child))
                child = child.next
        self._children = new_children
    
    def _get_element_type(self):
        return self._xml_root.name
    element_type = property(_get_element_type)
    
    def _find_nodes(self, root, elname = None, maxdepth = -1, **params):
        res = []
        if elname == None or root.name == elname:
            add = True
            for i in params:
                if root.prop(i) != params[i]:
                    add = False
                    break
            if add:
                res.append(root)
        if maxdepth != 0:
            child = root.children
            while child:
                res += self._find_nodes(child, elname, maxdepth - 1, **params)
                child = child.next
        return res
    
    def _get_title(self):
        nodes = self._find_nodes(self._xml_root, "title", 1)
        if len(nodes) == 1:
            return nodes[0].getContent()
    title = property(_get_title)
    
    def is_structure(self):
        return self.element_type in ["chapter"] or self.element_type.startswith("sect")
    
    def get_structure_tree(self):
        title = self.title
        if title == None:
            if self.filename:
                title = os.path.split(self.filename)[1]
            else:
                title = self.element_type
        res = {"id": self.object_id, "element_type": self.element_type, "edit_mode": self.edit_mode, "children": [], "label": title}
        for i in self._children:
            if i.is_structure():
                res["children"].append(i.get_structure_tree())
        return res
    
    def find_section_by_id(self, section_id):
        if section_id == self.object_id:
            return self
        else:
            for i in self._children:
                res = i.find_section_by_id(section_id)
                if res:
                    return res
    
    def find_by_node(self, node):
        if node == self._xml_root:
            return self
        else:
            for i in self._children:
                res = i.find_by_node(node)
                if res:
                    return res
    
    def _get_edit_mode(self):
        if self.element_type in EDIT_MODES:
            return EDIT_MODES[self.element_type]
        else:
            return None
    edit_mode = property(_get_edit_mode)
    
    def _warn_unconverted_docbook_node_type(self, node_type):
        if not node_type in self._already_warned_unconverted_docbook_node_type:
            self._already_warned_unconverted_docbook_node_type.append(node_type)
            logging.warn("Unconverted docbook node type : %s" % node_type)
    
    def _warn_unconverted_html_node_type(self, node_type):
        if not node_type in self._already_warned_unconverted_html_node_type:
            self._already_warned_unconverted_html_node_type.append(node_type)
            logging.warn("Unconverted HTML node type : %s" % node_type)
    
    def _warn_unconverted_docbook_prop(self, prop_name):
        if not prop_name in self._already_warned_unconverted_docbook_prop:
            self._already_warned_unconverted_docbook_prop.append(prop_name)
            logging.warn("Unconverted docbook property : %s" % prop_name)
 
    def _warn_unconverted_html_prop(self, prop_name):
        if not prop_name in self._already_warned_unconverted_html_prop:
            self._already_warned_unconverted_html_prop.append(prop_name)
            logging.warn("Unconverted HTML property : %s" % prop_name)
    
    def _docbook_to_html_process_properties(self, xml_node, html_node):
        prop = xml_node.get_properties()
        while prop:
            if prop.name in DOCBOOK_TO_HTML_PROPS:
                prop_value = xml_node.prop(prop.name)
                if prop.name == "fileref":
                    prop_value = urlparse.urljoin('file:', os.path.join(os.path.split(self.get_real_filename())[0], prop_value))
                html_node.setProp(DOCBOOK_TO_HTML_PROPS[prop.name], prop_value)
            else:
                self._warn_unconverted_docbook_prop(prop.name)
            prop = prop.next
    
    def _docbook_to_html_node(self, xml_node):
        if xml_node.name == "text":
            return xml_node.copyNode(False)
        elif xml_node.type == "entity_ref":
            return libxml2.newText(str(xml_node))
        elif xml_node.name in DOCBOOK_TO_HTML_NODES:
            res = self._docbook_to_html(xml_node)
            #~ if xml_node.name == "figure":
                #~ title_nodes = self._find_nodes(xml_node, "title", 1)
                #~ if len(title_nodes) == 1:
                    #~ img_nodes = self._find_nodes(res, "img")
                    #~ if len(img_nodes) == 1:
                        #~ img_nodes[0].setProp("alt", title_nodes[0].getContent())
            self._docbook_to_html_process_properties(xml_node, res)
            return res
        elif xml_node.name in DOCBOOK_JUMP_NODES:
            res = []
            subchild = xml_node.children
            while subchild:
                html_child = self._docbook_to_html_node(subchild)
                if type(html_child) == list:
                    res += html_child
                elif html_child != None:
                    res.append(html_child)
                subchild = subchild.next
            return res
        else:
            self._warn_unconverted_docbook_node_type(xml_node.name)
            return None
    
    def _docbook_to_html(self, xml_node, is_root = False):
        if xml_node.name == "title" and xml_node.parent.name == "figure":
            html_node = libxml2.newNode("figcaption")
        else:
            html_node = libxml2.newNode(DOCBOOK_TO_HTML_NODES[xml_node.name])
        self._docbook_to_html_process_properties(xml_node, html_node)
        if xml_node.name in DOCBOOK_ELEMENT_TYPE_TO_CLASS:
            html_node.newProp("class", xml_node.name)
            html_node.newProp("data-docbook-type", xml_node.name)
        child = xml_node.children
        while child:
            html_child = self._docbook_to_html_node(child)
            if type(html_child) == list:
                for i in html_child:
                    html_node.addChild(i)
            elif html_child != None:
                html_node.addChild(html_child)
            child = child.next
        return html_node
    
    def _html_to_docbook_node(self, html_node):
        if html_node.name == "text":
            return html_node.copyNode(False)
        #~ elif html_node.type == "entity_ref":
            #~ return libxml2.newText(str(html_node))
        elif html_node.name in ["div", "span"] and html_node.prop("data-docbook-type") in DOCBOOK_ELEMENT_TYPE_TO_CLASS:
            res = self._html_to_docbook(html_node)
            self._html_to_docbook_process_properties(html_node, res)
            return res
        elif html_node.name in HTML_TO_DOCBOOK_NODES:
            res = self._html_to_docbook(html_node)
            self._html_to_docbook_process_properties(html_node, res)
            return res
        elif html_node.name in HTML_JUMP_NODES:
            res = []
            subchild = html_node.children
            while subchild:
                xml_child = self._html_to_docbook_node(subchild)
                if type(xml_child) == list:
                    res += xml_child
                elif xml_child != None:
                    res.append(xml_child)
                subchild = subchild.next
            return res
        else:
            self._warn_unconverted_html_node_type(html_node.name)
            return None
    
    def _html_to_docbook(self, html_node):
        if html_node.name == "html":
            return self._html_to_docbook_node(html_node)[0]
        elif html_node.name in ["div", "span"] and html_node.prop("data-docbook-type") in DOCBOOK_ELEMENT_TYPE_TO_CLASS:
            if html_node.prop("data-section-id") and int(html_node.prop("data-section-id")) != self.object_id:
                section = self.find_section_by_id(int(html_node.prop("data-section-id")))
                if section:
                    return section.get_xml_node()
            xml_node = libxml2.newNode(html_node.prop("data-docbook-type"))
        else:
            xml_node = libxml2.newNode(HTML_TO_DOCBOOK_NODES[html_node.name])
        self._html_to_docbook_process_properties(html_node, xml_node)
        if html_node.name == "table":
            sub_xml_node = libxml2.newNode("tgroup")
            sub_xml_node.setProp("colsep", "1")
            sub_xml_node.setProp("rowsep", "1")
            sub_xml_node.setProp("align", "left")
            trs = self._find_nodes(html_node, "tr")
            if len(trs) > 0:
                sub_xml_node.setProp("cols", str(len(self._find_nodes(trs[0], "td"))))
            xml_node.addChild(sub_xml_node)
        else:
            sub_xml_node = None
        child = html_node.children
        while child:
            xml_child = self._html_to_docbook_node(child)
            if type(xml_child) == list:
                for i in xml_child:
                    if sub_xml_node:
                        sub_xml_node.addChild(i)
                    else:
                        xml_node.addChild(i)
            elif xml_child != None:
                if sub_xml_node:
                    sub_xml_node.addChild(xml_child)
                else:
                    xml_node.addChild(xml_child)
            child = child.next
        return xml_node
    
    def _html_to_docbook_process_properties(self, html_node, xml_node):
        prop = html_node.get_properties()
        while prop:
            if prop.name in HTML_TO_DOCBOOK_PROPS:
                prop_value = html_node.prop(prop.name)
                if prop.name == "src":
                    real_filename_uri = os.path.split(urlparse.urljoin('file:', self.get_real_filename()))[0] + "/"
                    if prop_value.startswith(real_filename_uri):
                        prop_value = prop_value[len(real_filename_uri):]
                xml_node.setProp(HTML_TO_DOCBOOK_PROPS[prop.name], prop_value)
            else:
                self._warn_unconverted_html_prop(prop.name)
            prop = prop.next
    
    def get_html(self, root = True):
        assert (self.edit_mode == "html")
        
        html_node = libxml2.newNode(DOCBOOK_TO_HTML_NODES[self._xml_root.name])
        html_node.newProp("data-docbook-type", self._xml_root.name)
        html_node.newProp("data-section-id", str(self.object_id))
        if not root:
            html_node.newProp("class", "%s mceNonEditable" % self._xml_root.name)
        self._docbook_to_html_process_properties(self._xml_root, html_node)
        for i in self._children:
            if (i.element_type in ["chapter"] or i.element_type.startswith("sect")):
                child_node = i.get_html(False)
            else:
                child_node = self._docbook_to_html_node(i.get_xml_node())
            if type(child_node) != list:
                child_node = [child_node]
            for j in child_node:
                html_node.addChild(j)
        
        return html_node
    
    def update_from_html(self, html):
        assert (self.edit_mode == "html")
        
        html_doc = libxml2.htmlParseDoc(html, "utf-8")
        new_xml_node = self._html_to_docbook(html_doc.getRootElement())
        self._xml_root.addNextSibling(new_xml_node)
        self._xml_root.unlinkNode()
        self._load_from_xml_object(new_xml_node)
    
    def save(self):
        self._xml_document.saveFormatFileEnc(self.filename, "utf-8", True)
        for i in self._children:
            if i.filename:
                i.save()
        self.store_saved_state()
    
    def _get_content_hash(self):
        md5 = hashlib.md5()
        md5.update(str(self._xml_root))
        hashsum = md5.digest()
        for i in self._children:
            if i.filename:
                hashsum += i.content_hash
        return hashsum
    content_hash = property(_get_content_hash)
    
    def store_saved_state(self):
        self._saved_state = self.content_hash
    
    def _get_changed(self):
        return self.content_hash != self._saved_state
    changed = property(_get_changed)
    
    def get_xml_node(self):
        return self._xml_root
