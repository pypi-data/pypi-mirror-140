# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
CORE-POS vendor item views
"""

from corepos.db.office_op import model as corepos

from .master import CoreOfficeMasterView


class VendorItemView(CoreOfficeMasterView):
    """
    Base class for vendor iem views.
    """
    model_class = corepos.VendorItem
    model_title = "CORE-POS Vendor Item"
    url_prefix = '/core-pos/vendor-items'
    route_prefix = 'corepos.vendor_items'

    labels = {
        'vendor_item_id': "ID",
        'sku': "SKU",
        'vendor_id': "Vendor ID",
        'upc': "UPC",
        'vendor_department_id': "Vendor Department ID",
        'srp': "SRP",
    }

    grid_columns = [
        'vendor_item_id',
        'sku',
        'vendor',
        'upc',
        'brand',
        'description',
        'size',
        'cost',
        'units',
        'modified',
    ]

    form_fields = [
        'vendor_item_id',
        'sku',
        'vendor_id',
        'vendor',
        'upc',
        'brand',
        'description',
        'size',
        'units',
        'cost',
        'sale_cost',
        'vendor_department_id',
        'srp',
        'modified',
    ]

    def configure_grid(self, g):
        super(VendorItemView, self).configure_grid(g)

        g.filters['upc'].default_active = True
        g.filters['upc'].default_verb = 'contains'

        g.set_type('units', 'quantity')

        g.set_sort_defaults('modified', 'desc')

        g.set_link('vendor_item_id')
        g.set_link('sku')
        g.set_link('vendor')
        g.set_link('upc')
        g.set_link('brand')
        g.set_link('description')

    def configure_form(self, f):
        super(VendorItemView, self).configure_form(f)

        f.set_type('units', 'quantity')
        f.set_type('srp', 'currency')

        f.set_readonly('vendor')

        if self.creating:
            f.remove('vendor_item_id')
        else:
            f.set_readonly('vendor_item_id')

        if self.creating or self.editing:
            f.remove('modified')
        else:
            f.set_readonly('modified')


def defaults(config, **kwargs):
    base = globals()

    VendorItemView = kwargs.get('VendorItemView', base['VendorItemView'])
    VendorItemView.defaults(config)


def includeme(config):
    defaults(config)
