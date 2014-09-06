# -*- coding=utf-8 -*-

import gtk

class OpenBookDialog(gtk.FileChooserDialog):
    def __init__(self, application, window):
        gtk.FileChooserDialog.__init__(self, parent = window, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    
    def run(self):
        self.show_all()
        if gtk.FileChooserDialog.run(self) == gtk.RESPONSE_OK:
            res = self.get_filename()
        else:
            res = None
        self.hide()
        return res
