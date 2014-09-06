# SaveQuitDialog.py
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

class SaveQuitDialog(gtk.MessageDialog):
    def __init__(self, parent):
        gtk.MessageDialog.__init__(self, parent, type = gtk.MESSAGE_QUESTION)
        
        self.set_title(_("Confirmation"))
        self.set_markup("<big><b>%s</b></big>" % _("Save before closing ?"))
        self.format_secondary_text(_("You have unsaved changes. These changes will be lost if you quit without saving."))
        
        self.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)
        self.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    
    def run(self):
        self.show_all()
        res = gtk.MessageDialog.run(self)
        self.hide()
        return res
