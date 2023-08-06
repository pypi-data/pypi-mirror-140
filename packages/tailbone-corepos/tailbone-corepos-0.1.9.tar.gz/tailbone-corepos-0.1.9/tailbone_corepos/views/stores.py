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
Store Views
"""

from tailbone.views import stores as base


class StoreView(base.StoreView):
    """
    Master view for the Store class.
    """
    labels = {
        'corepos_id': "CORE-POS ID",
    }

    @property
    def form_fields(self):
        fields = super(StoreView, self).form_fields
        return fields + [
            'corepos_id',
        ]

    def query(self, session):
        query = super(StoreView, self).query(session)
        model = self.model
        return query.outerjoin(model.CoreStore)

    def configure_grid(self, g):
        super(StoreView, self).configure_grid(g)
        model = self.model
        g.set_filter('corepos_id', model.CoreStore.corepos_id)

    def get_version_child_classes(self):
        model = self.model
        return super(StoreView, self).get_version_child_classes() + [
            model.CoreStore,
        ]


def includeme(config):
    StoreView.defaults(config)
