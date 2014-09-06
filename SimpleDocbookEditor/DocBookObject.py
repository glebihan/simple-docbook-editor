# -*- coding=utf-8 -*-

import libxml2
import os
import logging

OBJECT_IDS = 0

EDIT_MODES = {
    "book": "raw",
    "chapter": "html",
    "sect1": "html",
    "sect2": "html",
    "sect3": "html"
}

DOCBOOK_TO_HTML = {
    "chapter": "div",
    "sect1": "div",
    "sect2": "div",
    "sect3": "div",
    "note": "div",
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
    "ulink": "a"
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
]
DOCBOOK_JUMP_NODES = [
    "tgroup"
]

class DocBookObject(object):
    def __init__(self, **params):
        global OBJECT_IDS
        
        self._params = params
        
        self._already_warned_unconverted_docbook_node_type = []
        
        OBJECT_IDS += 1
        self.object_id = OBJECT_IDS
        
        assert ("filename" in self._params) or ("xml_object" in self._params)
        
        if "filename" in params and params["filename"] != None:
            self._load_from_file()
        else:
            self._load_from_xml_object(params["xml_object"])
    
    def _get_filename(self):
        return self._params.setdefault("filename", None)
    filename = property(_get_filename)
    
    def _load_from_file(self):
        logging.debug("Parsing file %s" % self.filename)
        
        self._xml_document = libxml2.parseFile(self.filename)
        self._load_from_xml_object(self._xml_document.getRootElement())
    
    def _load_from_xml_object(self, xml_object):
        self._xml_root = xml_object
        self._children = []
        if xml_object.children:
            child = xml_object.children
            while child:
                if child.name == "include":
                    include_filename = os.path.join(os.path.split(self.filename)[0], child.prop("href"))
                    if os.path.exists(include_filename):
                        self._children.append(DocBookObject(filename = include_filename))
                    else:
                        self._children.append(DocBookObject(xml_object = child))
                else:
                    self._children.append(DocBookObject(xml_object = child))
                child = child.next
    
    def _get_element_type(self):
        return self._xml_root.name
    element_type = property(_get_element_type)
    
    def _get_title(self):
        child = self._xml_root.children
        while child:
            if child.name == "title":
                return child.getContent()
            child = child.next
    title = property(_get_title)
    
    def is_structure(self):
        return self.element_type in ["chapter"] or self.element_type.startswith("sect")
    
    def get_structure_tree(self):
        title = self.title
        res = {"id": self.object_id, "element_type": self.element_type, "edit_mode": self.edit_mode, "children": [], "label": (self.element_type, title)[title != None]}
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
    
    def _docbook_to_html_node(self, xml_node):
        if xml_node.name == "text":
            return xml_node.copyNode(False)
        elif xml_node.name in DOCBOOK_TO_HTML:
            return self._docbook_to_html(xml_node)
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
    
    def _docbook_to_html(self, xml_node):
        html_node = libxml2.newNode(DOCBOOK_TO_HTML[xml_node.name])
        if xml_node.name in DOCBOOK_ELEMENT_TYPE_TO_CLASS:
            html_node.newProp("class", xml_node.name)
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
    
    def get_html(self):
        assert (self.edit_mode == "html")
        
        return self._docbook_to_html(self._xml_root)
