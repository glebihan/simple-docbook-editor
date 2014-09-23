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
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError
from distutils import log
import sys
import os
import commands
from SimpleDocbookEditor.informations import *

DEFAULT_EDITOR = "tinymce"

class build_tinymce(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # build tinymce
        if os.path.exists("share/simple-docbook-editor/tinymce"):
            if not is_newer_dir("tinymce", "share/simple-docbook-editor/tinymce"):
                log.info("Nothing to do")
                return
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

class build_jquery(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # build jquery
        if os.path.exists("share/simple-docbook-editor/jquery"):
            if not is_newer_dir("jquery", "share/simple-docbook-editor/jquery"):
                log.info("Nothing to do")
                return
            os.system("rm -rf share/simple-docbook-editor/jquery/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/jquery")
        os.chdir("jquery")
        os.system("npm run build")
        os.chdir("..")
        os.system("cp jquery/dist/jquery.min.js jquery/LICENSE.txt share/simple-docbook-editor/jquery")

class build_jqueryui(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # build jquery-ui
        if os.path.exists("share/simple-docbook-editor/jquery-ui"):
            if not is_newer_dir("jquery-ui", "share/simple-docbook-editor/jquery-ui"):
                log.info("Nothing to do")
                return
            os.system("rm -rf share/simple-docbook-editor/jquery-ui/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/jquery-ui")
        os.chdir("jquery-ui")
        os.system("npm install")
        os.system("../node_modules/.bin/grunt concat")
        os.chdir("..")
        os.system("cp -R jquery-ui/dist/* jquery-ui/LICENSE.txt share/simple-docbook-editor/jquery-ui")

class build_jqtree(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # package jqTree
        if os.path.exists("share/simple-docbook-editor/jqTree"):
            if not is_newer_dir("jqTree", "share/simple-docbook-editor/jqTree"):
                log.info("Nothing to do")
                return
            os.system("rm -rf share/simple-docbook-editor/jqTree/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/jqTree")
        os.system("cp -R jqTree/tree.jquery.js jqTree/LICENSE share/simple-docbook-editor/jqTree")

class build_codemirror(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # package CodeMirror
        if os.path.exists("share/simple-docbook-editor/CodeMirror"):
            if not is_newer_dir("CodeMirror", "share/simple-docbook-editor/CodeMirror"):
                log.info("Nothing to do")
                return
            os.system("rm -rf share/simple-docbook-editor/CodeMirror/*")
            os.system("mkdir -p share/simple-docbook-editor/CodeMirror/addon")
            os.system("mkdir -p share/simple-docbook-editor/CodeMirror/mode")
        else:
            os.system("mkdir -p share/simple-docbook-editor/CodeMirror/addon")
            os.system("mkdir -p share/simple-docbook-editor/CodeMirror/mode")
        os.chdir("CodeMirror")
        os.system("./bin/compress lib/codemirror.js > ../share/simple-docbook-editor/CodeMirror/codemirror.min.js")
        os.chdir("..")
        os.system("cp CodeMirror/lib/codemirror.css share/simple-docbook-editor/CodeMirror")
        os.system("cp CodeMirror/LICENSE share/simple-docbook-editor/CodeMirror")
        os.system("cp -R CodeMirror/addon/* share/simple-docbook-editor/CodeMirror/addon")
        os.system("cp -R CodeMirror/mode/* share/simple-docbook-editor/CodeMirror/mode")

class build_ckeditor(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # package ckeditor
        if os.path.exists("share/simple-docbook-editor/ckeditor"):
            if not is_newer_dir("ckeditor", "share/simple-docbook-editor/ckeditor"):
                log.info("Nothing to do")
                return
            os.system("rm -rf share/simple-docbook-editor/ckeditor/*")
        else:
            os.system("mkdir -p share/simple-docbook-editor/ckeditor")
        os.chdir("ckeditor")
        os.system("./dev/builder/build.sh")
        os.chdir("..")
        os.system("cp ckeditor/dev/builder/release/ckeditor/ckeditor.js share/simple-docbook-editor/ckeditor")

class build_editor(Command):
    user_options = [
        ('editor=', 'e', "editor to build")
    ]
    
    def initialize_options(self):
        self.editor = DEFAULT_EDITOR

    def finalize_options(self):
        if not self.editor in ["ckeditor", "tinymce"]:
            raise DistutilsOptionError("Supported editors are ckeditor and tinymce")

    def run(self):
        self.run_command("build_%s" % self.editor)
        
        js_build_variables = {
            "use_editor": self.editor
        }
        
        if self.editor == "tinymce":
            scripts = [
                "../tinymce/tinymce.min.js",
                "../tinymce-custom-plugins/docbook_subsections/plugin.js"
            ]
        else:
            scripts = [
                "../ckeditor/ckeditor.js"
            ]
            
        f = open("share/simple-docbook-editor/ui/main_window.html.in")
        html_data = f.read().replace("$EDITOR_SCRIPTS$", "\n        ".join(["<script type=\"text/javascript\" src=\"%s\"></script>" % s for s in scripts]))
        f.close()
        f = open("share/simple-docbook-editor/ui/main_window.html", "w")
        f.write(html_data)
        f.close()
        
        js_build_variables_list = []
        for i in js_build_variables:
            js_build_variables_list.append("var %s = \"%s\";" % (i, js_build_variables[i]))
        
        f = open("share/simple-docbook-editor/ui/main_window.js.in")
        html_data = f.read().replace("$BUILD_VARIABLES$", "\n".join(js_build_variables_list))
        f.close()
        f = open("share/simple-docbook-editor/ui/main_window.js", "w")
        f.write(html_data)
        f.close()

class update_pot(Command):
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.exists("l10n"):
            os.mkdir("l10n")
        os.system("xgettext -o l10n/%s.pot --from-code=utf-8 --package-name=\"%s\" --package-version=\"%s\" --copyright-holder=\"%s\" `find SimpleDocbookEditor -name '*.py'` `find share/simple-docbook-editor -name '*.js'`" % (UNIX_APPNAME, UNIX_APPNAME, VERSION, AUTHORS[0]["name"]))
    
class build(_build):
    user_options = _build.user_options + build_editor.user_options
    
    def initialize_options(self):
        _build.initialize_options(self)
        self.editor = DEFAULT_EDITOR
    
    def run(self):
        for cmd_name in self.get_sub_commands():
            if cmd_name == "build_editor":
                # Special case for the build_editor command, we need to pass it the editor parameter
                cmd_obj = self.distribution.get_command_obj(cmd_name)
                cmd_obj.editor = self.editor
                cmd_obj.ensure_finalized()
                cmd_obj.run()
            else:
                self.run_command(cmd_name)
        _build.run(self)
    
    sub_commands = [
        ("build_editor", None),
        ("build_jquery", None),
        ("build_jqueryui", None),
        ("build_jqtree", None),
        ("build_codemirror", None),
        ("update_pot", None)
    ]

def is_newer_dir(dir1, dir2):
    ts_dir1 = max([os.path.getmtime(f) for f in commands.getoutput("find \"%s\" -type f" % dir1).splitlines()])
    ts_dir2 = max([os.path.getmtime(f) for f in commands.getoutput("find \"%s\" -type f" % dir2).splitlines()])
    return ts_dir1 > ts_dir2

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
            if not i.endswith("~") and not i.endswith(".bak") and not i.endswith(".in") and os.path.isfile(os.path.join(dirpath, i)):
                dirfileslist.append(os.path.join(dirpath, i))
        if dirfileslist:
            res.append((dirpath, dirfileslist))
    return res

packages = list_packages()
package_dir = {}
for i in packages:
    package_dir[i] = i.replace(".", "/")

setup(
    cmdclass = {
        "build": build,
        "build_editor": build_editor,
        "build_tinymce": build_tinymce,
        "build_ckeditor": build_ckeditor,
        "build_jquery": build_jquery,
        "build_jqueryui": build_jqueryui,
        "build_jqtree": build_jqtree,
        "build_codemirror": build_codemirror,
        "update_pot": update_pot
    },
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
