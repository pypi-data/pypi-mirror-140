# -*- coding: utf-8; -*-
"""
Vendor Catalog Batch views for Corporal
"""

from corepos.db.office_op import model as corepos

from deform import widget as dfwidget

from tailbone.views.batch import vendorcatalog as base
from tailbone_corepos.db import CoreOfficeSession


class VendorCatalogView(base.VendorCatalogView):
    """
    Master view for vendor catalog batches.
    """
    form_fields = [
        'id',
        'description',
        'vendor_id',
        'vendor_name',
        'filename',
        'notes',
        'created',
        'created_by',
        'rowcount',
        'executed',
        'executed_by',
    ]

    def configure_form(self, f):
        super(VendorCatalogView, self).configure_form(f)
        model = self.model

        # vendor_id
        if self.creating:
            vendors = CoreOfficeSession.query(corepos.Vendor)\
                                       .order_by(corepos.Vendor.name)\
                                       .all()
            values = [(str(vendor.id), vendor.name)
                      for vendor in vendors]
            f.set_widget('vendor_id', dfwidget.SelectWidget(values=values))
            f.set_required('vendor_id')
            f.set_label('vendor_id', "Vendor")

        # vendor_name
        if self.creating:
            f.remove('vendor_name')

    def get_batch_kwargs(self, batch):
        kwargs = super(VendorCatalogView, self).get_batch_kwargs(batch)

        if 'vendor_name' not in kwargs and batch.vendor_id:
            vendor = CoreOfficeSession.query(corepos.Vendor).get(batch.vendor_id)
            if vendor:
                kwargs['vendor_name'] = vendor.name

        return kwargs


def includeme(config):
    VendorCatalogView.defaults(config)
