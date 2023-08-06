from .model import Field
from smartapi import base

import graphene

class FieldQuery(base.BaseType):

    class Meta:
        model = Field
        interfaces = (base.BaseRelayNode, )
        connection_class = base.BaseConnection
        login_required = True

    PERMISSIONS = ("ui.base",)
