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
Common views
"""

from tailbone.views import common as base

import messkit


class CommonView(base.CommonView):

    project_title = "messkit"
    project_version = messkit.__version__ + '+dev'


def includeme(config):
    CommonView.defaults(config)
