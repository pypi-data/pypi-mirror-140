from graphene.types.definitions import GrapheneObjectType
from graphene_django.types import DjangoObjectType, DjangoObjectTypeOptions
import graphene_django_optimizer as gql_optimizer
from rest_framework import serializers
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene import relay
from django.db import models
from django.utils import timezone
import json

from . import errors

import os

from graphql import GraphQLError

from graphene_django_cud import mutations
from graphene_django_cud.util import disambiguate_id

import types

from typing import Iterable

from graphene import Mutation
from graphene.types.mutation import MutationOptions
from graphql import GraphQLError

from graphene_django_cud.util import (
    get_likely_operation_from_name,
    disambiguate_id,
    get_fk_all_extras_field_names,
    get_m2m_all_extras_field_names,
    disambiguate_ids,
    is_field_many_to_many,
    is_field_one_to_one,
)

import graphene
from graphene import ObjectType, String, ID

from graphql_jwt.decorators import login_required

from django.core.files.storage import FileSystemStorage
from django.conf import settings

from django.utils.module_loading import import_string
Comp = import_string(settings.TENANT_MODEL)

from graphene_django.fields import DjangoConnectionField

from django.db.models import Q

import mimetypes

from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat

from django.core.exceptions import ValidationError

@deconstructible
class FileValidator(object):
    def get_content_types(self, type='*'):
        types = {
            'xlsx': 'application/vnd.ms-excel',
            'log': 'text/plain',
            'csv': 'text/csv',
            'xls': 'application/vnd.ms-excel',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'zip': 'application/zip',
            'pgp': 'application/pgp',
            'doc': 'text/plain',
            'gif': 'image/gif',
            'jpg': 'image/jpg',
            'htm': 'html',
            'html': 'html',
            'xlt': 'application/vnd.ms-excel',
            'png': 'image/png',
            'tif': 'image/tiff',
            'tiff': 'image/tiff',
            'jpeg': 'image/jpeg',
        }

        #todo filter from type

        return types

    error_messages = {
     'max_size': ("Ensure this file size is not greater than %(max_size)s."
                  " Your file size is %(size)s."),
     'min_size': ("Ensure this file size is not less than %(min_size)s. "
                  "Your file size is %(size)s."),
     'content_type': "Files of type %(content_type)s are not supported.",
    }

    def __str__(self):
        return self.content_types

    def __init__(self, max_size=None, min_size=None, type='*'):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = self.get_content_types(type)

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                'max_size': filesizeformat(self.max_size),
                'size': filesizeformat(data.size),
            }
            raise errors.ValidationError(self.error_messages['max_size'],
                                   'max_size', params)

        if self.min_size is not None and data.size < self.min_size:
            params = {
                'min_size': filesizeformat(self.min_size),
                'size': filesizeformat(data.size)
            }
            raise errors.ValidationError(self.error_messages['min_size'],
                                   'min_size', params)

        if self.content_types:
            content_type = mimetypes.guess_type(data.path)[0]

            if content_type not in self.content_types.values():
                params = { 'content_type': content_type }
                raise errors.ValidationError(self.error_messages['content_type'],
                                   'content_type', params)

    def __eq__(self, other):
        return (
            isinstance(other, FileValidator) and
            self.max_size == other.max_size and
            self.min_size == other.min_size and
            self.content_types == other.content_types
        )

def base_storage():
    return FileSystemStorage(location='')

def base_storage_path(instance, filename):
    return os.path.join(settings.STORAGE, instance.comp.comp_id, instance.sub_folder, filename)


class BaseModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'api'
        managed = False

    pass

from django.dispatch import receiver
from django.db.models.signals import pre_save
@receiver(pre_save)
def pre_save_handler(sender, instance, *args, **kwargs):
    instance.full_clean()


class BaseTenantModel(models.Model):
    class Meta:
        abstract = True
        app_label = 'api'
        managed = False

    tenant_id = 'comp_id'
    comp = models.ForeignKey(
        Comp,
        verbose_name='Company',
        editable=False,
        default='', #this is to prevent graphql from saying comp is required
        on_delete=models.CASCADE
    )

    pass

class TimestampMixin(models.Model):
    class Meta:
        abstract = True
        app_label = 'api'
        managed = False

    create_username = models.CharField(
        verbose_name='Created By',
        max_length=256,
        default='system'
    )
    create_date = models.DateTimeField(
        verbose_name='Created On',
        auto_now_add=True,
    )

    mod_username = models.CharField(
        verbose_name='Modified By',
        max_length=256,
        default='system',
        null=True,
        blank=True
    )

    mod_date = models.DateTimeField(
        verbose_name='Modified On',
        auto_now=True,
        null=True,
        blank=True
    )

    pass

class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True
        app_label = 'api'
        managed = False

    deleted_date = models.DateTimeField(
        verbose_name='Deleted On',
        blank=True,
        null=True
    )

    def delete(self):
        self.deleted_date = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()

    pass

def set_input_context(info, d, add_create = True):
    if add_create:
        d['create_username'] = str(info.context.user.username)
    d['mod_username'] = str(info.context.user.username)
    d['comp'] = info.context.user.comp_id

    for k, v in d.items():
        if isinstance(v, dict):
            set_input_context(info, v, add_create)
        elif type(v) == type([]):
            for a in v:
                if isinstance(a, dict):
                    set_input_context(info, a, add_create)

class BaseRelayNode(graphene.relay.Node):
    class Meta:
        name = 'Node'

    @staticmethod
    def to_global_id(type_, id):
        return id

    @staticmethod
    def get_node_from_global_id(info, global_id, only_type=None):
        model = only_type._meta.model
        return model.objects.get(pk=global_id)


class BaseCreateMutation(mutations.DjangoCreateMutation):
    class Meta:
        abstract = True

    @classmethod
    def check_permissions(cls, root, info, *args, **kwargs) -> None:
        if hasattr(cls, 'PERMISSIONS') and len(cls.PERMISSIONS) > 0:
            if info.context.user.is_anonymous:
                raise errors.UnauthorizedError()
            elif not info.context.user.has_perms(cls.PERMISSIONS):
                raise errors.ForbidenError()

    @classmethod
    def before_mutate(cls, root, info, input):
        set_input_context(info, input)
        return input


class BaseUpdateMutation(mutations.DjangoPatchMutation):
    class Meta:
        abstract = True

    @classmethod
    def check_permissions(cls, root, info, *args, **kwargs) -> None:
        if hasattr(cls, 'PERMISSIONS') and len(cls.PERMISSIONS) > 0:
            if info.context.user.is_anonymous:
                raise errors.UnauthorizedError()
            elif not info.context.user.has_perms(cls.PERMISSIONS):
                raise errors.ForbidenError()

    @classmethod
    def before_mutate(cls, root, info, input, id):
        set_input_context(info, input, add_create = False)

        return input


class BaseDeleteMutation(mutations.DjangoDeleteMutation):
    class Meta:
        abstract = True

    @classmethod
    def check_permissions(cls, root, info, *args, **kwargs) -> None:
        if hasattr(cls, 'PERMISSIONS') and len(cls.PERMISSIONS) > 0:
            if info.context.user.is_anonymous:
                raise errors.UnauthorizedError()
            elif not info.context.user.has_perms(cls.PERMISSIONS):
                raise errors.ForbidenError()

class BaseConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    total_count=graphene.Int()

    def resolve_total_count(self, *_) -> int:
        return self.length


class BaseType(DjangoObjectType):
    class Meta:
        abstract = True

    node_description = String()

    def resolve_node_description(parent, info):
        return parent.__str__()

    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):

        if hasattr(cls, 'PERMISSIONS') and len(cls.PERMISSIONS) > 0:
            if info.context.user.is_anonymous:
                raise errors.UnauthorizedError()
            elif not info.context.user.has_perms(cls.PERMISSIONS):
                raise errors.ForbidenError()

        if queryset.__class__.__name__ == 'Manager' :
            queryset = gql_optimizer.query(cls._meta.model.objects.all(), info)

        if hasattr(cls._meta.model, 'tenant_id'):
            queryset = queryset.filter(**{cls._meta.model.tenant_id: info.context.user.comp});

        if hasattr(cls._meta.model, 'deleted_date'):
            queryset = queryset.filter(deleted_date__isnull=True);

        return queryset

class BaseField(DjangoConnectionField):
    @classmethod
    def resolve_queryset(cls, connection, queryset, info, args):
        qs = super().resolve_queryset(connection, queryset, info, args)

        order = args.get('order', None)
        if order:
            qs = qs.order_by(*order)

        filters = args.get('filters', None)
        if filters:
            for filter in filters:
                q_objects = Q()

                if filter.or_filters:
                    for condition in filter.or_filters:
                        if(condition.field[-6:] == 'isnull'):
                            condition.qs = condition.qs == "true"
                        elif(condition.field[-4:] == '__in'):
                            condition.qs = json.loads(condition.qs)


                        q_objects |= Q(**{condition.field: condition.qs})

                if filter.and_filters:
                    for condition in filter.and_filters:
                        if(condition.field[-6:] == 'isnull'):
                            condition.qs = condition.qs == "true"
                        elif(condition.field[-4:] == '__in'):
                            condition.qs = json.loads(condition.qs)

                        q_objects &= Q(**{condition.field: condition.qs})

                qs = qs.filter(q_objects)

        # mine = args.get('mine', None)
        # if mine:
        #     query = Q()
        #     query |= Q(owner_sec_user=info.context.user)
        #     departments = info.context.user.sec_user_department_set.values_list('department__id', flat=True)
        #     query |= Q(owner_department__in=departments)
        #
        #     qs = qs.filter(query)

        return qs

class SearchFieldObjectType(graphene.InputObjectType):
    field=of_type=graphene.String()
    qs=graphene.String()

class SearchObjectType(graphene.InputObjectType):
    and_filters=graphene.List(of_type=SearchFieldObjectType)
    or_filters=graphene.List(of_type=SearchFieldObjectType)

DefaultFieldArgs = {
    'order': graphene.List(of_type=graphene.String),
    'filters': graphene.List(of_type=SearchObjectType),
}
