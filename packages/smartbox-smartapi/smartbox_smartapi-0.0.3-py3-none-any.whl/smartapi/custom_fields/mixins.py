import graphene
from django.db import models
from .model import Field
from .data.row.model import FieldDataRow
from .data.value.model import FieldDataValue
from graphene_django_cud.util import disambiguate_id

class CustomFieldQuery(graphene.InputObjectType):
    field = graphene.ID()
    value = graphene.String()

class CustomFieldMixin(models.Model):
    class Meta:
        abstract = True
        app_label = 'api'
        managed = False

    field_data_row = models.OneToOneField(
        FieldDataRow,
        verbose_name='Custom Field',
        on_delete=models.RESTRICT,
        null=True, blank=True
    )


class CreateMutation():
    class Meta:
        abstract = True

    @classmethod
    def before_save(cls, root, info, input, obj):
        if input.get("customFields"):
            field_data_row = FieldDataRow.objects.create(comp=info.context.user.comp)
            field_data_row.save()
            obj.field_data_row = field_data_row

            for field in input.get("customFields"):
                FieldDataValue.objects.create(comp=info.context.user.comp, create_username = info.context.user.username, mod_username = info.context.user.username, field_data_row=field_data_row, field=Field(pk=disambiguate_id(field.field)), value=field.value)

        return obj

class UpdateMutation():
    class Meta:
        abstract = True

    @classmethod
    def before_save(cls, root, info, input, id, obj):
        if input.get("customFields"):
            if not obj.field_data_row:
                field_data_row = FieldDataRow.objects.create(comp=info.context.user.comp)
                field_data_row.save()
                obj.field_data_row = field_data_row

            for field in input.get("customFields"):

                if len(FieldDataValue.objects.filter(field_data_row__exact=obj.field_data_row, field__exact=Field(pk=disambiguate_id(field.field)))) == 0:
                    FieldDataValue.objects.create(comp=info.context.user.comp, create_username = info.context.user, mod_username = info.context.user.username, field_data_row=obj.field_data_row , field=Field(pk=disambiguate_id(field.field)), value=field.value)
                else:
                    field_data_value = FieldDataValue.objects.get(field_data_row=obj.field_data_row , field=Field(pk=disambiguate_id(field.field)))
                    field_data_value.value = field.value
                    field_data_value.mod_username = info.context.user.username
                    field_data_value.save()

        return obj
