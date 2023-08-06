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
messkit web app
"""

from tailbone import app


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    # prefer messkit templates over Tailbone
    settings.setdefault('mako.directories', ['messkit.web:templates',
                                             'tailbone:templates',])

    # for graceful handling of postgres restart
    settings.setdefault('retry.attempts', 2)

    # make config objects
    rattail_config = app.make_rattail_config(settings)
    pyramid_config = app.make_pyramid_config(settings)

    # bring in the rest of messkit
    pyramid_config.include('messkit.web.static')
    pyramid_config.include('messkit.web.subscribers')
    pyramid_config.include('messkit.web.views')

    # for graceful handling of postgres restart
    pyramid_config.add_tween('tailbone.tweens.sqlerror_tween_factory',
                             under='pyramid_tm.tm_tween_factory')

    return pyramid_config.make_wsgi_app()
