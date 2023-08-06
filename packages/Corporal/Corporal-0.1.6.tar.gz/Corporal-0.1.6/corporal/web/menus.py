# -*- coding: utf-8; -*-
"""
Corporal Web Menus
"""

from tailbone_corepos.menus import make_corepos_menu


def simple_menus(request):
    url = request.route_url

    corepos_menu = make_corepos_menu(request)

    batch_menu = {
        'title': "Batches",
        'type': 'menu',
        'items': [
            {
                'title': "CORE Member",
                'url': url('batch.coremember'),
                'perm': 'batch.coremember.list',
            },
            {
                'title': "Vendor Catalogs",
                'url': url('vendorcatalogs'),
                'perm': 'vendorcatalogs.list',
            },
        ],
    }

    reports_menu = {
        'title': "Reports",
        'type': 'menu',
        'items': [
            {
                'title': "New Report",
                'route': 'report_output.create',
                'perm': 'report_output.create',
            },
            {
                'title': "Generated Reports",
                'route': 'report_output',
                'perm': 'report_output.list',
            },
            {
                'title': "Problem Reports",
                'route': 'problem_reports',
                'perm': 'problem_reports.list',
            },
            {'type': 'sep'},
            {
                'title': "Poser Reports",
                'route': 'poser.reports',
                'perm': 'poser.reports.list',
            },
        ],
    }

    admin_menu = {
        'title': "Admin",
        'type': 'menu',
        'items': [
            {
                'title': "Users",
                'url': url('users'),
                'perm': 'users.list',
            },
            {
                'title': "User Events",
                'url': url('userevents'),
                'perm': 'userevents.list',
            },
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
            {
                'title': "Email Attempts",
                'url': url('email_attempts'),
                'perm': 'email_attempts.list',
            },
            {
                'title': "Raw Settings",
                'url': url('settings'),
                'perm': 'settings.list',
            },
            {'type': 'sep'},
            {
                'title': "Tables",
                'url': url('tables'),
                'perm': 'tables.list',
            },
            {
                'title': "Importing / Exporting",
                'url': url('importing'),
                'perm': 'importing.runjobs',
            },
            {
                'title': "Corporal Upgrades",
                'url': url('upgrades'),
                'perm': 'upgrades.list',
            },
        ],
    }

    menus = [
        corepos_menu,
        batch_menu,
        reports_menu,
        admin_menu,
    ]

    return menus
