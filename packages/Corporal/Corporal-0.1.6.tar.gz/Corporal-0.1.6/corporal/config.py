"""
Custom config
"""

from rattail.config import ConfigExtension


class CorporalConfig(ConfigExtension):
    """
    Rattail config extension for Corporal
    """
    key = 'corporal'

    def configure(self, config):

        if config.getbool('rattail.config', 'corporal.set_defaults',
                          usedb=False, default=True):

            # set some default config values
            config.setdefault('rattail', 'model', 'corporal.db.model')
            config.setdefault('rattail.mail', 'emails', 'corporal.emails')
            config.setdefault('rattail', 'settings', 'corporal.settings')
            config.setdefault('tailbone', 'menus', 'corporal.web.menus')
            config.setdefault('rattail.config', 'templates', 'corporal:data/config rattail:data/config')

            # batches
            config.setdefault('rattail.batch', 'vendor_catalog.handler', 'corporal.batch.vendorcatalog:VendorCatalogHandler')
