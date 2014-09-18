# MainWindow.py
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

import gtk
import webkit
import os
import urlparse
import urllib
import json
import logging
from OpenBookDialog import OpenBookDialog
from ImageBrowserDialog import ImageBrowserDialog
from AboutDialog import AboutDialog
from SaveQuitDialog import SaveQuitDialog
from ..informations import *

class MainWindow(object):
    def __init__(self, application):
        self._application = application
        
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(self._application.cli_options.share_dir, UNIX_APPNAME, "ui", "ui.glade"))
        self._window = builder.get_object("main_window")
        self._window.add_accel_group(builder.get_object("main_accelgroup"))
        
        self._window.set_title(_(APPNAME))
        
        self._window.set_size_request(self._application.config["UI/width"], self._application.config["UI/height"])
        self._maximized = self._application.config["UI/maximized"]
        if self._maximized:
            self._window.maximize()
        
        self._webview = webkit.WebView()
        builder.get_object("webview_container").add(self._webview)
        self._webview.get_settings().set_property('enable-file-access-from-file-uris', 1)
        self._webview.get_settings().set_property('enable-default-context-menu', 0)
        self._webview.connect("script-alert", self._on_webview_script_alert)
        self._webview_load_finished = False
        self._webview_pending_commands = []
        
        self._statusbar = builder.get_object("statusbar")
        
        self._load_main_window()
        
        self._window.connect("delete_event", self._on_window_delete_event)
        builder.get_object("quit_menu_item").connect("activate", self._on_quit_clicked)
        builder.get_object("open_book_menuitem").connect("activate", self._on_open_book_clicked)
        builder.get_object("save_book_menuitem").connect("activate", self._on_save_book_clicked)
        builder.get_object("close_book_menuitem").connect("activate", self._on_close_book_clicked)
        builder.get_object("about_menuitem").connect("activate", self._on_about_clicked)
        
        self._open_book_dialog = OpenBookDialog(self._application, self._window)
        self._about_dialog = AboutDialog(self._window)
        self._save_quit_dialog = SaveQuitDialog(self._window)
        self._image_browser_dialog = ImageBrowserDialog(self._application, self._window)
        
        self._mapped = False
        self._window.connect("size-allocate", self._on_size_allocate)
        self._window.connect("window-state-event", self._on_window_state_event)
        self._window.connect("map-event", self._on_map_event)
    
    def _on_map_event(self, window, event):
        self._mapped = True
        self._window.connect("size-allocate", self._on_size_allocate)
        self._window.connect("window-state-event", self._on_window_state_event)
    
    def _on_window_state_event(self, window, event):
        if self._mapped:
            self._maximized = (event.new_window_state & gtk.gdk.WINDOW_STATE_MAXIMIZED != 0)
    
    def _on_size_allocate(self, window, rectangle):
        if self._mapped:
            if self._maximized:
                self._application.config["UI/maximized"] = True
            else:
                self._application.config["UI/maximized"] = False
                width, height = self._window.get_size()
                self._application.config["UI/width"] = width
                self._application.config["UI/height"] = height
    
    def _check_quit(self):
        if self._application.book and self._application.book.changed:
            resp = self._save_quit_dialog.run()
            if resp == gtk.RESPONSE_YES:
                self._application.book.save()
            elif resp != gtk.RESPONSE_NO:
                return True
        gtk.main_quit()
        return False
    
    def _on_window_delete_event(self, window, event):
        return self._check_quit()
    
    def _on_close_book_clicked(self, menuitem):
        if self._application.book:
            if self._application.book.changed:
                resp = self._save_quit_dialog.run()
                if resp == gtk.RESPONSE_YES:
                    self._application.book.save()
                elif resp != gtk.RESPONSE_NO:
                    return
            self._application.unload_book()
            self.send_command("set_doc_structure(null)")
    
    def _on_about_clicked(self, menuitem):
        self._about_dialog.run()
        
    def _on_quit_clicked(self, menuitem):
        self._check_quit()
    
    def _on_open_book_clicked(self, menuitem):
        filename = self._open_book_dialog.run()
        if filename:
            if self._application.book:
                self._on_close_book_clicked(menuitem)
            if self._application.book:
                return
            self._application.load_book(filename)
    
    def _on_save_book_clicked(self, menuitem):
        self._application.book.save()
    
    def show_all(self):
        self._window.show_all()
    
    def _do_send_command(self, command):
        self._webview.execute_script(command)
    
    def send_command(self, command):
        if self._webview_load_finished:
            self._do_send_command(command)
        else:
            self._webview_pending_commands.append(command)
    
    def _on_webview_script_alert(self, editor, frame, message):
        logging.debug("_on_webview_script_alert:%s" % ":".join(message.split(":")[:2]))
        
        if ":" in message:
            i = message.index(":")
            command = message[:i]
            params = message[i+1:]
        else:
            command = message
            params = ""
        
        if command == "reload_doc_structure":
            if self._application.book:
                self.send_command("set_doc_structure(%s)" % json.dumps(self._application.book.get_structure_tree()))
        elif command == "editor_ready":
            while len(self._webview_pending_commands):
                command = self._webview_pending_commands[0]
                del self._webview_pending_commands[0]
                self._do_send_command(command)
            self._webview_load_finished = True
        elif command == "load_doc_section":
            section_id = int(params)
            section = self._application.book.find_section_by_id(section_id)
            xml = section.get_xml_text()
            if section.edit_mode == "html":
                self.send_command("set_edit_data(%s)" % json.dumps({"section_id": section_id, "edit_mode": section.edit_mode, "html": str(section.get_html()), "xml": str(xml)}))
            else:
                self.send_command("set_edit_data(%s)" % json.dumps({"section_id": section_id, "edit_mode": section.edit_mode, "xml": str(xml)}))
        elif command == "set_section_contents":
            i = params.index(":")
            section_id = int(params[:i])
            contents = params[i+1:]
            section = self._application.book.find_section_by_id(section_id)
            parsing_error = section.update_from_html(contents)
            if parsing_error:
                parsing_error_json = json.dumps(_("You have an error in your document. Please fix it before editing another section."))
            else:
                parsing_error_json = json.dumps(None)
            self.send_command("set_parsing_error(%s)" % parsing_error_json)
            self.send_command("set_doc_structure(%s)" % json.dumps(self._application.book.get_structure_tree()))
        elif command == "set_section_source_contents":
            i = params.index(":")
            section_id = int(params[:i])
            contents = params[i+1:]
            section = self._application.book.find_section_by_id(section_id)
            parsing_error = section.update_from_xml(contents)
            if parsing_error:
                parsing_error_json = json.dumps(_("You have an error in your document. Please fix it before editing another section."))
            else:
                parsing_error_json = json.dumps(None)
            self.send_command("set_parsing_error(%s)" % parsing_error_json)
            self.send_command("set_doc_structure(%s)" % json.dumps(self._application.book.get_structure_tree()))
        elif command == "browse_image":
            i = params.index(":")
            field_name = params[:i] 
            url = params[i+1:]
            if url:
                filename = urllib.url2pathname(url)[7:]
            else:
                filename = None
            new_filename = self._image_browser_dialog.run(filename)
            if new_filename:
                self.send_command("set_file_browser_filename(%s)" % json.dumps({"field_name": field_name, "url": urlparse.urljoin('file:', urllib.pathname2url(new_filename))}))
        elif command == "load_config":
            self._do_send_command("set_config(%s)" % json.dumps(self._application.config.serialize()))
        elif command == "translate":
            self.send_command("set_translation(%s)" % json.dumps({"mesg": params, "translation": _(params)}))
        else:
            return False
            
        return True
    
    def _load_main_window(self):
        filename = os.path.join(self._application.cli_options.share_dir, UNIX_APPNAME, "ui", "main_window.html")
        f = open(filename)
        data = f.read()
        f.close()
        
        while "_(" in data:
            i = data.index("_(")
            pcount = 1
            j = i + 2
            while pcount != 0:
                if data[j] == "(":
                    pcount += 1
                if data[j] == ")":
                    pcount -= 1
                j += 1
            data = data[:i] + _(data[i+2:j-1]) + data[j:]
        
        self._webview.load_html_string(data, urlparse.urljoin('file:', urllib.pathname2url(filename)))
    
    def refresh_view_for_new_book(self, section_id = 0):
        self.send_command("refresh_view_for_new_book(%d)" % section_id)
        if self._application.book:
            self._window.set_title("%s - %s" % (_(APPNAME), self._application.book.filename))
        else:
            self._window.set_title("%s" % _(APPNAME))
