from .model import FieldDataRow
from smartapi import base

import graphene

class FieldDataRowQuery(base.BaseType):
    class Meta:
        model = FieldDataRow
        interfaces = (base.BaseRelayNode, )
        connection_class = base.BaseConnection
        login_required = True

    PERMISSIONS = ("ui.base",)
