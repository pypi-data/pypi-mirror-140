# -*- coding: utf-8; -*-
"""
Common views
"""

from tailbone.views import common as base

import corporal


class CommonView(base.CommonView):

    project_title = "Corporal"
    project_version = corporal.__version__ + '+dev'


def includeme(config):
    CommonView.defaults(config)
