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
Person views
"""

from rattail_corepos.config import core_office_customer_account_url

from tailbone.views import people as base


class PersonView(base.PersonView):
    """
    Expose some extra fields etc. per CORE-POS integration.

    Please note that this does include a bit of "business logic" which assumes
    that you keep CORE and Rattail in sync!  Use at your own risk.
    """
    labels = {
        'corepos_customer_id': "CORE-POS Customer ID",
    }

    @property
    def form_fields(self):
        fields = super(PersonView, self).form_fields
        return fields + [
            'corepos_customer_id',
        ]

    def query(self, session):
        query = super(PersonView, self).query(session)
        model = self.rattail_config.get_model()
        return query.outerjoin(model.CorePerson)

    def configure_grid(self, g):
        super(PersonView, self).configure_grid(g)
        model = self.rattail_config.get_model()
        g.set_filter('corepos_customer_id', model.CorePerson.corepos_customer_id)

    def configure_form(self, f):
        super(PersonView, self).configure_form(f)

        # corepos_customer_id
        if self.creating:
            f.remove('corepos_customer_id')
        elif self.editing:
            f.set_required('corepos_customer_id', False)

    def get_version_child_classes(self):
        model = self.rattail_config.get_model()
        return super(PersonView, self).get_version_child_classes() + [
            model.CorePerson,
        ]

    def get_context_customers(self, person):
        data = super(PersonView, self).get_context_customers(person)

        # add CORE Office URL for each customer account
        for customer in data:
            customer['view_corepos_url'] = core_office_customer_account_url(
                self.rattail_config, customer['number'])

        return data

    def get_context_member(self, member):
        data = super(PersonView, self).get_context_member(member)

        # add CORE Office URL for member account
        data['view_corepos_url'] = core_office_customer_account_url(
            self.rattail_config, member['number'])

        return data


def includeme(config):
    PersonView.defaults(config)
