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
Web Menus
"""


def simple_menus(request):
    url = request.route_url

    # reports_menu = {
    #     'title': "Reports",
    #     'type': 'menu',
    #     'items': [
    #         {
    #             'title': "New Report",
    #             'url': url('report_output.create'),
    #             'perm': 'report_output.create',
    #         },
    #         {
    #             'title': "Generated Reports",
    #             'url': url('report_output'),
    #             'perm': 'report_output.list',
    #         },
    #         {
    #             'title': "Problem Reports",
    #             'url': url('problem_reports'),
    #             'perm': 'problem_reports.list',
    #         },
    #     ],
    # }

    # other_menu = {
    #     'title': "Other",
    #     'type': 'menu',
    #     'items': [
    #         {
    #             'title': "Generate New Feature",
    #             'url': url('generate_feature'),
    #             'perm': 'common.generate_feature',
    #         },
    #         {
    #             'title': "Generate New Project",
    #             'url': url('generate_project'),
    #             'perm': 'common.generate_project',
    #         },
    #     ],
    # }

    admin_menu = {
        'title': "Admin",
        'type': 'menu',
        'items': [
            {
                'title': "Users",
                'url': url('users'),
                'perm': 'users.list',
            },
            # {
            #     'title': "User Events",
            #     'url': url('userevents'),
            #     'perm': 'userevents.list',
            # },
            {
                'title': "Roles",
                'url': url('roles'),
                'perm': 'roles.list',
            },
            {'type': 'sep'},
            {
                'title': "App Settings",
                'url': url('appsettings'),
                'perm': 'settings.list',
            },
            {
                'title': "Email Settings",
                'url': url('emailprofiles'),
                'perm': 'emailprofiles.list',
            },
            # {
            #     'title': "Email Attempts",
            #     'url': url('email_attempts'),
            #     'perm': 'email_attempts.list',
            # },
            {
                'title': "Raw Settings",
                'url': url('settings'),
                'perm': 'settings.list',
            },
            {'type': 'sep'},
            # {
            #     'title': "DataSync Changes",
            #     'url': url('datasyncchanges'),
            #     'perm': 'datasync_changes.list',
            # },
            # {
            #     'title': "Importing / Exporting",
            #     'url': url('importing'),
            #     'perm': 'importing.list',
            # },
            {
                'title': "Tables",
                'url': url('tables'),
                'perm': 'tables.list',
            },
            {
                'title': "messkit Upgrades",
                'url': url('upgrades'),
                'perm': 'upgrades.list',
            },
        ],
    }

    menus = [
        # reports_menu,
        # other_menu,
        admin_menu,
    ]

    return menus
