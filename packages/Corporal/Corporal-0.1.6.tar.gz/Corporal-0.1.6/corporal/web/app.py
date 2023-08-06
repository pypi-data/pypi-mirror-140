# -*- coding: utf-8; -*-
"""
Corporal web app
"""

from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import register

from tailbone import app
from tailbone_corepos.db import (CoreOfficeSession, CoreTransSession,
                                 ExtraCoreOfficeSessions, ExtraCoreTransSessions)


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    # prefer Corporal templates over Tailbone
    settings.setdefault('mako.directories', ['corporal.web:templates',
                                             'tailbone_corepos:templates',
                                             'tailbone:templates'])

    # make config objects
    rattail_config = app.make_rattail_config(settings)
    pyramid_config = app.make_pyramid_config(settings)

    # CORE-POS DB(s)
    CoreOfficeSession.configure(bind=rattail_config.corepos_engine)
    CoreTransSession.configure(bind=rattail_config.coretrans_engine)

    # create session wrappers for each "extra" CORE DB engine
    for key, engine in rattail_config.corepos_engines.items():
        if key != 'default':
            Session = scoped_session(sessionmaker(bind=engine))
            register(Session)
            ExtraCoreOfficeSessions[key] = Session

    # create session wrappers for each "extra" CORE Transaction DB engine
    for key, engine in rattail_config.coretrans_engines.items():
        if key != 'default':
            Session = scoped_session(sessionmaker(bind=engine))
            register(Session)
            ExtraCoreTransSessions[key] = Session

    # bring in the rest of Corporal
    pyramid_config.include('corporal.web.static')
    pyramid_config.include('corporal.web.subscribers')
    pyramid_config.include('corporal.web.views')

    return pyramid_config.make_wsgi_app()
