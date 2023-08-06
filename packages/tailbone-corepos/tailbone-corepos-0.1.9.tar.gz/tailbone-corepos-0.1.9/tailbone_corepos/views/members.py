# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
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
Member Views
"""

from tailbone.views import members as base


class MemberView(base.MemberView):
    """
    Master view for the Member class.
    """

    labels = {
        'corepos_account_id': "CORE-POS Account ID",
    }

    @property
    def form_fields(self):
        fields = super(MemberView, self).form_fields
        return fields + [
            'corepos_account_id',
        ]

    def query(self, session):
        query = super(MemberView, self).query(session)
        model = self.rattail_config.get_model()
        return query.outerjoin(model.CoreMember)

    def configure_grid(self, g):
        super(MemberView, self).configure_grid(g)
        model = self.rattail_config.get_model()
        g.set_filter('corepos_account_id', model.CoreMember.corepos_account_id)

    def get_version_child_classes(self):
        model = self.rattail_config.get_model()
        return super(MemberView, self).get_version_child_classes() + [
            model.CoreMember,
        ]


def includeme(config):
    MemberView.defaults(config)
