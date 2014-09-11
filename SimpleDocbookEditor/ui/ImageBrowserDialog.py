# ImageBrowserDialog.py
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

class ImageBrowserDialog(gtk.FileChooserDialog):
    def __init__(self, application, window):
        gtk.FileChooserDialog.__init__(self, parent = window, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        file_filter = gtk.FileFilter()
        file_filter.add_mime_type("image/*")
        file_filter.set_name(_("Image Files"))
        self.add_filter(file_filter)
    
    def run(self, filename):
        if filename:
            self.set_filename(filename)
        self.show_all()
        if gtk.FileChooserDialog.run(self) == gtk.RESPONSE_OK:
            res = self.get_filename()
        else:
            res = None
        self.hide()
        return res
