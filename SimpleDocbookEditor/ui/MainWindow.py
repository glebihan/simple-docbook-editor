# -*- coding=utf-8 -*-

import gtk
import webkit
import os
import urlparse
import urllib
import json
from OpenBookDialog import OpenBookDialog

class MainWindow(object):
    def __init__(self, application):
        self._application = application
        
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(self._application.cli_options.share_dir, "simple-docbook-editor", "ui", "ui.glade"))
        self._window = builder.get_object("main_window")
        self._window.add_accel_group(builder.get_object("main_accelgroup"))
        
        self._window.set_title(_("Simple DocBook Editor"))
        
        self._window.set_size_request(640, 480)
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
        
        self._open_book_dialog = OpenBookDialog(self._application, self._window)
    
    def _check_quit(self):
        gtk.main_quit()
        return False
    
    def _on_window_delete_event(self, window, event):
        return self._check_quit()
    
    def _on_quit_clicked(self, menuitem):
        self._check_quit()
    
    def _on_open_book_clicked(self, menuitem):
        filename = self._open_book_dialog.run()
        if filename:
            self._application.load_book(filename)
    
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
            if section.edit_mode == "html":
                self.send_command("set_edit_data(%s)" % json.dumps({"edit_mode": "html", "html": str(section.get_html())}))
        else:
            return False
            
        return True
    
    def _load_main_window(self):
        filename = os.path.join(self._application.cli_options.share_dir, "simple-docbook-editor", "ui", "main_window.html")
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
    
    def refresh_view_for_new_book(self):
        self.send_command("refresh_view_for_new_book()")
