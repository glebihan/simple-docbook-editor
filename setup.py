#! /usr/bin/env python
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-
# setup.py
#
# Copyright © 2014 Gwendal Le Bihan
# 
# This file is part of simple-docbook-editor.
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

from distutils.command.build import build as _build
from distutils.core import setup
import sys, os
from SimpleDocbookEditor.informations import *

class build(_build):
    def run(self):
        # build tinymce
        if os.path.exists("share/simple-docbook-editor/tinymce"):
            os.system("rm -rf share/simple-docbook-editor/tinymce/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/tinymce")
        for custom_plugin in os.listdir("tinymce-plugins-overrides"):
            if os.path.exists("tinymce/js/tinymce/plugins/%s" % custom_plugin):
                os.system("mv \"tinymce/js/tinymce/plugins/%s\" \"tinymce/js/tinymce/plugins/%s.orig\"" % (custom_plugin, custom_plugin))
            os.system("cp -R \"tinymce-plugins-overrides/%s\" tinymce/js/tinymce/plugins" % custom_plugin)
        os.chdir("tinymce")
        os.system("npm install")
        os.system("jake")
        os.chdir("..")
        os.system("cp -R tinymce/js/tinymce share/simple-docbook-editor")
        os.system("cp -R tinymce/LICENSE.TXT share/simple-docbook-editor/tinymce")
        os.system("rm -rf share/simple-docbook-editor/tinymce/plugins/*.orig")
        for custom_plugin in os.listdir("tinymce-plugins-overrides"):
            os.system("rm -rf \"tinymce/js/tinymce/plugins/%s\"" % custom_plugin)
            if os.path.exists("tinymce/js/tinymce/plugins/%s.orig" % custom_plugin):
                os.system("mv \"tinymce/js/tinymce/plugins/%s.orig\" \"tinymce/js/tinymce/plugins/%s\"" % (custom_plugin, custom_plugin))

        # build jquery
        if os.path.exists("share/simple-docbook-editor/jquery"):
            os.system("rm -rf share/simple-docbook-editor/jquery/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/jquery")
        os.chdir("jquery")
        os.system("npm run build")
        os.chdir("..")
        os.system("cp jquery/dist/jquery.min.js jquery/LICENSE.txt share/simple-docbook-editor/jquery")

        # build jquery-ui
        if os.path.exists("share/simple-docbook-editor/jquery-ui"):
            os.system("rm -rf share/simple-docbook-editor/jquery-ui/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/jquery-ui")
        os.chdir("jquery-ui")
        os.system("npm install")
        os.system("../node_modules/.bin/grunt concat")
        os.chdir("..")
        os.system("cp -R jquery-ui/dist/* jquery-ui/LICENSE.txt share/simple-docbook-editor/jquery-ui")

        # package jqTree
        if os.path.exists("share/simple-docbook-editor/jqTree"):
            os.system("rm -rf share/simple-docbook-editor/jqTree/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/jqTree")
        os.system("cp -R jqTree/tree.jquery.js jqTree/LICENSE share/simple-docbook-editor/jqTree")
        
        # package CodeMirror
        if os.path.exists("share/simple-docbook-editor/CodeMirror"):
            os.system("rm -rf share/simple-docbook-editor/CodeMirror/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/CodeMirror")
        os.chdir("CodeMirror")
        os.system("./bin/compress lib/codemirror.js > ../share/simple-docbook-editor/CodeMirror/codemirror.min.js")
        os.chdir("..")
        os.system("cp CodeMirror/lib/codemirror.css share/simple-docbook-editor/CodeMirror")
        os.system("cp CodeMirror/LICENSE share/simple-docbook-editor/CodeMirror")
        
        _build.run(self)

def list_packages():
    res = ['SimpleDocbookEditor']
    for dirpath, dirnames, filenames in os.walk('SimpleDocbookEditor'):
        for dirname in dirnames:
            if os.path.exists(os.path.join(dirpath, dirname, '__init__.py')):
                res.append(os.path.join(dirpath, dirname).replace("/", "."))
    return res
      
def list_share_files():
    res = []
    for dirpath, dirnames, filenames in os.walk('share'):
        dirfileslist = []
        for i in filenames:
            if not i.endswith("~") and not i.endswith(".bak") and os.path.isfile(os.path.join(dirpath, i)):
                dirfileslist.append(os.path.join(dirpath, i))
        if dirfileslist:
            res.append((dirpath, dirfileslist))
    return res

packages = list_packages()
package_dir = {}
for i in packages:
    package_dir[i] = i.replace(".", "/")

setup(
    cmdclass = {'build': build},
    name = UNIX_APPNAME,
    version = VERSION,
    author = AUTHORS[0]["name"],
    author_email = AUTHORS[0]["email"],
    maintainer = AUTHORS[0]["name"],
    maintainer_email = AUTHORS[0]["email"],
    description = APP_DESCRIPTION,
    scripts = ["simple-docbook-editor"],
    packages = packages,
    package_dir = package_dir,
    data_files = list_share_files()
)
