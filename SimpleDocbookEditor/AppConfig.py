# AppConfig.py
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

import ConfigParser
import os

CONFIG_TYPES = {
    "Source Editor/lineWrapping": bool,
    "UI/maximized": bool,
    "UI/width": int,
    "UI/height": int
}

DEFAULT_VALUES = {
    "Source Editor/lineWrapping": False,
    "UI/maximized": True,
    "UI/width": 800,
    "UI/height": 600
}

class AppConfig(object):
    def __init__(self, config_file):
        self._config_file = config_file
        self._config_parser = ConfigParser.RawConfigParser()
        self._config_parser.read(config_file)
    
    def _split_key(self, key):
        if "/" in key:
            section, option = key.split("/")
        else:
            section = "General"
            option = key
            key = section + "/" + option
        return section, option, key
    
    def __getitem__(self, key):
        section, option, key = self._split_key(key)
        if self._config_parser.has_option(section, option):
            conf_type = CONFIG_TYPES.setdefault(key, None)
            if conf_type == bool:
                return self._config_parser.getboolean(section, option)
            elif conf_type == int:
                return self._config_parser.getint(section, option)
            elif conf_type == float:
                return self._config_parser.getfloat(section, option)
            else:
                return self._config_parser.get(section, option)
        else:
            return DEFAULT_VALUES.setdefault(key, None)
    
    def __setitem__(self, key, value):
        section, option, key = self._split_key(key)
        if not self._config_parser.has_section(section):
            self._config_parser.add_section(section)
        self._config_parser.set(section, option, value)
        self._save()
    
    def _rec_mkdir(self, path):
        if os.path.exists(path):
            return
        
        self._rec_mkdir(os.path.split(path)[0])
        os.mkdir(path)
    
    def _save(self):
        self._rec_mkdir(os.path.split(self._config_file)[0])
        with open(self._config_file, "wb") as fd:
            self._config_parser.write(fd)
