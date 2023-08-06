# -*- coding: utf-8; -*-
"""
Corporal Views
"""


def includeme(config):

    # core views
    config.include('corporal.web.views.common')
    config.include('tailbone.views.auth')
    config.include('tailbone.views.tables')
    config.include('tailbone.views.upgrades')
    config.include('tailbone.views.progress')
    config.include('tailbone.views.importing')
    config.include('tailbone.views.poser')
    config.include('tailbone.views.reports')

    # main table views
    config.include('tailbone.views.email')
    config.include('tailbone_corepos.views.people')
    config.include('tailbone.views.roles')
    config.include('tailbone.views.settings')
    config.include('tailbone.views.users')

    # CORE-POS direct data views
    config.include('tailbone_corepos.views.corepos')

    # batches
    config.include('corporal.web.views.batch.vendorcatalog')
    config.include('tailbone_corepos.views.batch.coremember')
