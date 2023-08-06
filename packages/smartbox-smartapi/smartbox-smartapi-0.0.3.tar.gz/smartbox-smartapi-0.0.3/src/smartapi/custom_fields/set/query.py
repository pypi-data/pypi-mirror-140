from .model import FieldSet
from smartapi import base

import graphene

class FieldSetQuery(base.BaseType):
    class Meta:
        model = FieldSet
        interfaces = (base.BaseRelayNode, )
        connection_class = base.BaseConnection
        login_required = True

    PERMISSIONS = ("ui.base",)
