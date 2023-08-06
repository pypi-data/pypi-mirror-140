# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
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
Customer Views
"""

from tailbone.views import customers as base


class CustomerView(base.CustomerView):
    """
    Master view for the Customer class.
    """

    labels = {
        'corepos_account_id': "CORE-POS Account ID",
    }

    @property
    def form_fields(self):
        fields = super(CustomerView, self).form_fields
        return fields + [
            'corepos_account_id',
        ]

    def query(self, session):
        query = super(CustomerView, self).query(session)
        model = self.rattail_config.get_model()
        return query.outerjoin(model.CoreCustomer)

    def configure_grid(self, g):
        super(CustomerView, self).configure_grid(g)
        model = self.rattail_config.get_model()
        g.set_filter('corepos_account_id', model.CoreCustomer.corepos_account_id)

    def configure_form(self, f):
        super(CustomerView, self).configure_form(f)
        f.set_required('corepos_account_id', False)

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        customer = form.model_instance

        # this field lives in an extension table, but the column does not allow
        # null, which means we don't want to pass an empty value along unless
        # there is already an extension record in place for this customer
        if 'corepos_account_id' in data and data['corepos_account_id'] is None:
            if self.creating:
                data.pop('corepos_account_id')
            elif self.editing and not customer._corepos:
                data.pop('corepos_account_id')

        return super(CustomerView, self).objectify(form, data)

    def get_version_child_classes(self):
        model = self.rattail_config.get_model()
        return super(CustomerView, self).get_version_child_classes() + [
            model.CoreCustomer,
        ]


def includeme(config):
    CustomerView.defaults(config)
    base.PendingCustomerView.defaults(config)
