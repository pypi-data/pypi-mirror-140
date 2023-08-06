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
messkit Data Model
"""

from rattail.db.model import *

try:
    from poser.db.model import *
except ImportError:
    pass
