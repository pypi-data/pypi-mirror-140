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
Subdepartment Views
"""

from rattail_corepos.config import core_office_url

from tailbone.views import subdepartments as base


class SubdepartmentView(base.SubdepartmentView):
    """
    Master view for the Subdepartment class.
    """
    labels = {
        'corepos_number': "CORE-POS Number",
    }

    @property
    def form_fields(self):
        fields = super(SubdepartmentView, self).form_fields
        return fields + [
            'corepos_number',
        ]

    def query(self, session):
        query = super(SubdepartmentView, self).query(session)
        model = self.rattail_config.get_model()
        return query.outerjoin(model.CoreSubdepartment)

    def configure_grid(self, g):
        super(SubdepartmentView, self).configure_grid(g)
        model = self.rattail_config.get_model()
        g.set_filter('corepos_number', model.CoreSubdepartment.corepos_number)

    def get_version_child_classes(self):
        model = self.rattail_config.get_model()
        return super(SubdepartmentView, self).get_version_child_classes() + [
            model.CoreSubdepartment,
        ]


def includeme(config):
    SubdepartmentView.defaults(config)
