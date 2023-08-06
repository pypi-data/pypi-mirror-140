from .model import FieldDataValue
from smartapi import base
from graphene_django import DjangoObjectType

import graphene

class FieldDataValueQuery(base.BaseType):
    class Meta:
        model = FieldDataValue
        login_required = True
        fields = "__all__"

    PERMISSIONS = ("ui.base",)
