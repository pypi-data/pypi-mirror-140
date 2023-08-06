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
CORE-POS vendor views
"""

from corepos.db.office_op import model as corepos

from .master import CoreOfficeMasterView


class VendorView(CoreOfficeMasterView):
    """
    Base class for vendor views.
    """
    model_class = corepos.Vendor
    model_key = 'id'
    model_title = "CORE-POS Vendor"
    url_prefix = '/core-pos/vendors'
    route_prefix = 'corepos.vendors'
    creatable = True
    editable = True
    deletable = True

    labels = {
        'id': "ID",
    }

    grid_columns = [
        'id',
        'name',
        'abbreviation',
        'discount_rate',
        'contact',
    ]

    form_fields = [
        'id',
        'name',
        'abbreviation',
        'discount_rate',
        'phone',
        'fax',
        'email',
        'website',
        'notes',
    ]

    def configure_grid(self, g):
        super(VendorView, self).configure_grid(g)

        # TODO: this is only needed b/c of orm.synonym usage
        g.set_sorter('id', corepos.Vendor.id)

        g.set_link('id')
        g.set_link('name')
        g.set_link('abbreviation')

    # TODO: ugh, would be nice to not have to do this...
    def get_action_route_kwargs(self, row):
        return {'id': row.id}

    def configure_form(self, f):
        super(VendorView, self).configure_form(f)

        if self.creating:
            f.remove_field('contact')

    def core_office_object_url(self, office_url, vendor):
        return '{}/item/vendors/VendorIndexPage.php?vid={}'.format(
            office_url, vendor.id)


def defaults(config, **kwargs):
    base = globals()

    VendorView = kwargs.get('VendorView', base['VendorView'])
    VendorView.defaults(config)


def includeme(config):
    defaults(config)
