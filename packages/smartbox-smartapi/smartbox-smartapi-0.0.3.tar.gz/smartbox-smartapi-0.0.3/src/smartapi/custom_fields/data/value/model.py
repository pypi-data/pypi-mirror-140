from django.db import models

from smartapi import base

from ..row.model import FieldDataRow
from ...model import Field

class FieldDataValue(base.TimestampMixin, base.BaseTenantModel):
    class Meta:
        db_table = 'field_data_value'
        verbose_name = 'Data Value'
        verbose_name_plural = 'Data Values'
        default_related_name = 'field_data_value_set'

    id = models.AutoField(primary_key=True, db_column='field_data_value_id')

    field_data_row = models.ForeignKey(
        FieldDataRow,
        verbose_name='FieldDataRow',
        on_delete=models.CASCADE
    )

    field = models.ForeignKey(
        Field,
        verbose_name='Field',
        on_delete=models.CASCADE
    )

    value = models.CharField(max_length=2000, blank=True, null=True)
