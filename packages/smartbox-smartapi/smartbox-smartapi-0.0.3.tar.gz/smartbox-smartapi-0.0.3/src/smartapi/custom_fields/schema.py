import logging

from smartapi import base, custom_fields

from .query import FieldQuery
from .set.query import FieldSetQuery

from .data.row.query import FieldDataRowQuery
from .data.value.query import FieldDataValueQuery

import graphene
from graphene_django.filter import DjangoFilterConnectionField


class Query(object):

    field = base.BaseRelayNode.Field(FieldQuery)
    field_set = base.BaseField(FieldQuery, **base.DefaultFieldArgs)

    fieldset = base.BaseRelayNode.Field(FieldSetQuery)
    fieldset_set = base.BaseField(FieldSetQuery, **base.DefaultFieldArgs)

    field_data_row = base.BaseRelayNode.Field(FieldDataRowQuery)
    field_data_row_set = base.BaseField(FieldDataRowQuery, **base.DefaultFieldArgs)
