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
CORE-POS misc. utilities
"""

import logging

import sqlalchemy as sa

from corepos.db.office_op import Session as CoreSession, model as corepos

from rattail.db.util import short_session
from rattail.util import OrderedDict, progress_loop


log = logging.getLogger(__name__)


def get_core_members(api, progress=None):
    """
    Shared logic for fetching *all* customer accounts from CORE-POS API.
    """
    # TODO: ideally could do this, but API doesn't let us fetch "all"
    # return api.get_members()

    # first we fetch all customer records from CORE DB
    with short_session(Session=CoreSession) as s:
        db_customers = s.query(corepos.CustData).all()
        s.expunge_all()

    # now we must fetch each customer account individually from API
    members = OrderedDict()

    def fetch(dbcust, i):
        if dbcust.card_number in members:
            return          # already fetched this one
        member = api.get_member(dbcust.card_number)
        if member:
            members[dbcust.card_number] = member
        else:
            logger = log.warning if dbcust.person_number == 1 else log.debug
            logger("could not fetch member from CORE API: %s",
                   dbcust.card_number)

    progress_loop(fetch, db_customers, progress,
                  message="Fetching Member data from CORE API")
    return list(members.values())


def get_max_existing_vendor_id(session=None):
    """
    Returns the "last" (max) existing value for the ``vendors.vendorID``
    column, for use when creating new records, since it is not auto-increment.
    """
    with short_session(Session=CoreSession, session=session) as s:
        return s.query(sa.func.max(corepos.Vendor.id))\
                .scalar() or 0
