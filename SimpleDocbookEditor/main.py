# main.py
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

from ui.MainWindow import MainWindow
from DocBookObject import DocBookObject
from AppConfig import AppConfig
import gtk
import logging
import optparse
import os
from informations import *

DEBUG_LEVELS = {
   0: logging.FATAL,
   1: logging.ERROR,
   2: logging.WARNING,
   3: logging.INFO,
   4: logging.DEBUG
}

class SimpleDocbookEditor(object):
    def __init__(self):
        self._parse_cli_options()
        self._load_config()
        self._init_logger()
        
        self.book = None
        
        self._window = MainWindow(self)
    
    def _load_config(self):
        self.config = AppConfig(self.cli_options.config_file)
    
    def _parse_cli_options(self):
        optparser = optparse.OptionParser()
        optparser.add_option("--share-dir", dest = "share_dir", default = "/usr/share")
        optparser.add_option('-c', '--config-file', dest = "config_file", default = os.path.join(os.getenv("HOME"), ".config", UNIX_APPNAME, UNIX_APPNAME + ".conf"))
        optparser.add_option("--section-id", dest = "section_id", type = "int", default = 0)
        optparser.add_option("-d", "--debug-level", dest = "debug_level", type = "int", default = 2)
        self.cli_options, self.files_to_open = optparser.parse_args()
        
        self.cli_options.share_dir = os.path.realpath(self.cli_options.share_dir)
        self.cli_options.config_file = os.path.realpath(self.cli_options.config_file)
            
    def _init_logger(self):
        logging.getLogger().setLevel(DEBUG_LEVELS[self.cli_options.debug_level])
    
    def load_book(self, filename, section_id = 0):
        self.book = DocBookObject(filename = filename)
        self.book.store_saved_state()
        self._window.refresh_view_for_new_book(section_id)
    
    def unload_book(self):
        self.book = None
        self._window.refresh_view_for_new_book()
    
    def run(self):
        assert (len(self.files_to_open) <= 1)
        if len(self.files_to_open) == 1:
            self.load_book(os.path.realpath(self.files_to_open[0]), self.cli_options.section_id)
        self._window.show_all()
        gtk.main()
