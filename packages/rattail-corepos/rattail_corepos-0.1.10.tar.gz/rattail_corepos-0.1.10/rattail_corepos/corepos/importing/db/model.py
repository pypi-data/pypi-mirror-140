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
CORE-POS model importers (direct DB)

.. warning::
   All classes in this module are "direct DB" importers, which will write
   directly to MySQL.  They are meant to be used in dry-run mode only, and/or
   for sample data import to a dev system etc.  They are *NOT* meant for
   production use, as they will completely bypass any CORE business rules logic
   which may exist.
"""

from sqlalchemy.orm.exc import NoResultFound

from rattail import importing

from corepos.db.office_op import model as corepos
from corepos.db.office_trans import model as coretrans


class ToCore(importing.ToSQLAlchemy):
    """
    Base class for all CORE "operational" model importers.
    """

    def create_object(self, key, host_data):

        # NOTE! some tables in CORE DB may be using the MyISAM storage engine,
        # which means it is *not* transaction-safe and therefore we cannot rely
        # on "rollback" if in dry-run mode!  in other words we better not touch
        # the record at all, for dry run
        if self.dry_run:
            return host_data

        return super(ToCore, self).create_object(key, host_data)

    def update_object(self, obj, host_data, **kwargs):

        # NOTE! some tables in CORE DB may be using the MyISAM storage engine,
        # which means it is *not* transaction-safe and therefore we cannot rely
        # on "rollback" if in dry-run mode!  in other words we better not touch
        # the record at all, for dry run
        if self.dry_run:
            return obj

        return super(ToCore, self).update_object(obj, host_data, **kwargs)

    def delete_object(self, obj):

        # NOTE! some tables in CORE DB may be using the MyISAM storage engine,
        # which means it is *not* transaction-safe and therefore we cannot rely
        # on "rollback" if in dry-run mode!  in other words we better not touch
        # the record at all, for dry run
        if self.dry_run:
            return True

        return super(ToCore, self).delete_object(obj)


class ToCoreTrans(importing.ToSQLAlchemy):
    """
    Base class for all CORE "transaction" model importers
    """


########################################
# CORE Operational
########################################

class DepartmentImporter(ToCore):
    model_class = corepos.Department
    key = 'number'


class SubdepartmentImporter(ToCore):
    model_class = corepos.Subdepartment
    key = 'number'


class VendorImporter(ToCore):
    model_class = corepos.Vendor
    key = 'id'


class VendorContactImporter(ToCore):
    model_class = corepos.VendorContact
    key = 'vendor_id'


class ProductImporter(ToCore):
    model_class = corepos.Product
    key = 'id'


class ProductFlagImporter(ToCore):
    model_class = corepos.ProductFlag
    key = 'bit_number'


class VendorItemImporter(ToCore):
    model_class = corepos.VendorItem
    key = ('sku', 'vendor_id')


class EmployeeImporter(ToCore):
    model_class = corepos.Employee
    key = 'number'


class CustDataImporter(ToCore):
    model_class = corepos.CustData
    key = 'id'


class MemberTypeImporter(ToCore):
    model_class = corepos.MemberType
    key = 'id'


class MemberInfoImporter(ToCore):
    model_class = corepos.MemberInfo
    key = 'card_number'


class MemberDateImporter(ToCore):
    model_class = corepos.MemberDate
    key = 'card_number'


class MemberContactImporter(ToCore):
    model_class = corepos.MemberContact
    key = 'card_number'


class HouseCouponImporter(ToCore):
    model_class = corepos.HouseCoupon
    key = 'coupon_id'


########################################
# CORE Transactions
########################################

class TransactionDetailImporter(ToCoreTrans):
    """
    CORE-POS transaction data importer.
    """
    model_class = coretrans.TransactionDetail
