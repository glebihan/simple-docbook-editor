# AboutDialog.py
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
from ..informations import *

class AboutDialog(gtk.AboutDialog):
    def __init__(self, window):
        gtk.AboutDialog.__init__(self)
        self.set_transient_for(window)
        
        self.set_name(UNIX_APPNAME)
        self.set_program_name(APPNAME)
        self.set_version(VERSION)
        self.set_copyright(COPYRIGHT_NOTICE)
        self.set_comments(APP_DESCRIPTION)
        self.set_license(LICENSE)
        self.set_authors(["%s <%s>" % (a["name"], a["email"]) for a in AUTHORS])
    
    def run(self):
        self.show_all()
        gtk.AboutDialog.run(self)
        self.hide()
