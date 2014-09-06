# -*- coding=utf-8 -*-

from ui.MainWindow import MainWindow
from DocBookObject import DocBookObject
import gtk
import logging
import optparse
import os

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
        self._init_logger()
        
        self._window = MainWindow(self)
    
    def _parse_cli_options(self):
        optparser = optparse.OptionParser()
        optparser.add_option("--share-dir", dest = "share_dir", default = "/usr/share")
        optparser.add_option("--section-id", dest = "section_id", type = "int", default = 0)
        optparser.add_option("-d", "--debug-level", dest = "debug_level", type = "int", default = 2)
        self.cli_options, self.files_to_open = optparser.parse_args()
        
        self.cli_options.share_dir = os.path.realpath(self.cli_options.share_dir)
            
    def _init_logger(self):
        logging.getLogger().setLevel(DEBUG_LEVELS[self.cli_options.debug_level])
    
    def load_book(self, filename, section_id = 0):
        self.book = DocBookObject(filename = filename)
        self._window.refresh_view_for_new_book(section_id)
    
    def run(self):
        assert (len(self.files_to_open) <= 1)
        if len(self.files_to_open) == 1:
            self.load_book(os.path.realpath(self.files_to_open[0]), self.cli_options.section_id)
        self._window.show_all()
        gtk.main()
