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
Product Views
"""

from rattail_corepos.config import core_office_url

from tailbone.views import products as base


class ProductView(base.ProductView):
    """
    Master view for the Product class.
    """
    labels = {
        'corepos_id': "CORE-POS ID",
    }

    @property
    def form_fields(self):
        fields = super(ProductView, self).form_fields
        return self.corepos_add_form_fields(fields)

    def corepos_add_form_fields(self, fields):
        fields.extend([
            'corepos_id',
        ])
        return fields

    def query(self, session):
        query = super(ProductView, self).query(session)
        return self.corepos_modify_query(query)

    def corepos_modify_query(self, query):
        model = self.rattail_config.get_model()
        return query.outerjoin(model.CoreProduct)

    def configure_grid(self, g):
        super(ProductView, self).configure_grid(g)
        self.corepos_configure_grid(g)

    def corepos_configure_grid(self, g):
        model = self.rattail_config.get_model()
        g.set_filter('corepos_id', model.CoreProduct.corepos_id)

    def configure_form(self, f):
        super(ProductView, self).configure_form(f)
        self.corepos_configure_form(f)

    def corepos_configure_form(self, f):
        f.set_required('corepos_id', False)
        if self.creating:
            f.remove('corepos_id')

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        product = super(ProductView, self).objectify(form, data)
        return self.corepos_objectify(product)

    def corepos_objectify(self, product):
        # remove the corepos extension record outright, if we just lost the ID
        if product._corepos and not product.corepos_id:
            self.Session.delete(product._corepos)
            self.Session.flush()
        return product

    def get_version_child_classes(self):
        classes = super(ProductView, self).get_version_child_classes()
        return self.corepos_add_version_classes(classes)

    def corepos_add_version_classes(self, classes):
        model = self.rattail_config.get_model()
        classes.extend([
            model.CoreProduct,
        ])
        return classes

    def template_kwargs_view(self, **kwargs):
        kwargs = super(ProductView, self).template_kwargs_view(**kwargs)
        return self.corepos_template_kwargs_view(**kwargs)

    def corepos_template_kwargs_view(self, **kwargs):
        """
        Adds the URL for viewing the product within CORE Office, or else the
        reason for lack of such a URL.
        """
        product = kwargs['instance']

        # CORE Office URL
        kwargs['core_office_url'] = None
        office_url = core_office_url(self.rattail_config)
        if not office_url:
            kwargs['core_office_why_no_url'] = "CORE Office URL is not configured"
        else:
            kwargs['core_office_url'] = '{}/item/ItemEditorPage.php?searchupc={}'.format(
                office_url, product.item_id)

        return kwargs


# TODO: this seems awkward here, but makes things less awkward to
# modules using this one as their base
PendingProductView = base.PendingProductView


def includeme(config):
    ProductView.defaults(config)
    PendingProductView.defaults(config)
