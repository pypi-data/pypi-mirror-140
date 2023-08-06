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
Department Views
"""

from rattail_corepos.config import core_office_url

from tailbone.views import departments as base


class DepartmentView(base.DepartmentView):
    """
    Master view for the Department class.
    """
    labels = {
        'corepos_number': "CORE-POS Number",
    }

    @property
    def form_fields(self):
        fields = super(DepartmentView, self).form_fields
        return fields + [
            'corepos_number',
        ]

    def query(self, session):
        query = super(DepartmentView, self).query(session)
        model = self.rattail_config.get_model()
        return query.outerjoin(model.CoreDepartment)

    def configure_grid(self, g):
        super(DepartmentView, self).configure_grid(g)
        model = self.rattail_config.get_model()
        g.set_filter('corepos_number', model.CoreDepartment.corepos_number)

    def get_version_child_classes(self):
        model = self.rattail_config.get_model()
        return super(DepartmentView, self).get_version_child_classes() + [
            model.CoreDepartment,
        ]

    def template_kwargs_view(self, **kwargs):
        """
        Supplements the default logic as follows:

        Adds the URL for viewing the department within CORE Office, or else the
        reason for lack of such a URL.
        """
        # invoke default/parent logic, if it exists
        parent = super(DepartmentView, self)
        if hasattr(parent, 'template_kwargs_view'):
            kwargs = parent.template_kwargs_view(**kwargs)

        department = kwargs['instance']

        # CORE Office URL
        kwargs['core_office_url'] = None
        office_url = core_office_url(self.rattail_config)
        if not office_url:
            kwargs['core_office_why_no_url'] = "CORE Office URL is not configured"
        else:
            kwargs['core_office_url'] = '{}/item/departments/DepartmentEditor.php?did={}'.format(
                office_url, department.number)

        return kwargs


def includeme(config):
    DepartmentView.defaults(config)
