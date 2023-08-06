# -*- coding: utf-8; -*-
######################################################################
#
#  messkit -- Generic-ish Data Utility App
#  Copyright © 2022 Lance Edgar
#
#  This file is part of messkit.
#
#  messkit is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  messkit is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with messkit.  If not, see <http://www.gnu.org/licenses/>.
#
######################################################################
"""
Config extension for messkit
"""

import os
import sys

from rattail.config import ConfigExtension


class MesskitConfig(ConfigExtension):
    """
    Rattail config extension for messkit
    """
    key = 'messkit'

    def configure(self, config):

        # set some default config values
        config.setdefault('rattail', 'app_title', "messkit")
        config.setdefault('tailbone', 'menus', 'messkit.web.menus')
        config.setdefault('rattail', 'model', 'messkit.db.model')
        config.setdefault('rattail', 'settings', 'messkit.appsettings')

        # # always try to append poser to path
        # # TODO: location of poser dir should come from config/app/handler?
        # poser = os.path.join(sys.prefix, 'app', 'poser')
        # if poser not in sys.path and os.path.isdir(poser):
        #     sys.path.append(poser)
