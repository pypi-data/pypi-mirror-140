# -*- coding: utf-8; -*-
"""
App Settings
"""

from rattail.settings import Setting


# bring in some common settings from rattail
from rattail.settings import (

    # (General)
    rattail_app_title,
    tailbone_background_color,

    # Email
    rattail_mail_record_attempts,

    # Product
    rattail_product_key,
    rattail_product_key_title,
    tailbone_products_show_pod_image,

    # Purchasing / Receiving
    rattail_batch_purchase_allow_cases,
    rattail_batch_purchase_allow_expired_credits,
)
