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
Vendor views
"""

from rattail_corepos.config import core_office_url

from tailbone.views import vendors as base


class VendorView(base.VendorView):
    """
    Expose some extra fields etc. per CORE-POS integration.

    Please note that this does include a bit of "business logic" which assumes
    that you keep CORE and Rattail in sync!  Use at your own risk.
    """
    labels = {
        'corepos_id': "CORE-POS ID",
    }

    @property
    def form_fields(self):
        fields = super(VendorView, self).form_fields
        return fields + [
            'corepos_id',
        ]

    def query(self, session):
        query = super(VendorView, self).query(session)
        model = self.rattail_config.get_model()
        return query.outerjoin(model.CoreVendor)

    def configure_grid(self, g):
        super(VendorView, self).configure_grid(g)
        model = self.rattail_config.get_model()
        g.set_filter('corepos_id', model.CoreVendor.corepos_id)

    def get_version_child_classes(self):
        model = self.rattail_config.get_model()
        return super(VendorView, self).get_version_child_classes() + [
            model.CoreVendor,
        ]

    def template_kwargs_view(self, **kwargs):
        """
        Supplements the default logic as follows:

        Adds the URL for viewing the vendor within CORE Office, or else the
        reason for lack of such a URL.
        """
        # invoke default/parent logic, if it exists
        parent = super(VendorView, self)
        if hasattr(parent, 'template_kwargs_view'):
            kwargs = parent.template_kwargs_view(**kwargs)

        vendor = kwargs['instance']

        # CORE Office URL
        kwargs['core_office_url'] = None
        office_url = core_office_url(self.rattail_config)
        if not office_url:
            kwargs['core_office_why_no_url'] = "CORE Office URL is not configured"
        elif not vendor.corepos_id:
            kwargs['core_office_why_no_url'] = "Vendor has no CORE-POS ID"
        else:
            kwargs['core_office_url'] = '{}/item/vendors/VendorIndexPage.php?vid={}'.format(
                office_url, vendor.corepos_id)

        return kwargs


def includeme(config):
    VendorView.defaults(config)
