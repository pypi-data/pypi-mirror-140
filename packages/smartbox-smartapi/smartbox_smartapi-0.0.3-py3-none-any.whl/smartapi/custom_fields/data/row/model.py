from django.db import models

from smartapi import base

class FieldDataRow(base.TimestampMixin, base.BaseTenantModel):
    class Meta:
        db_table = 'field_data_row'
        verbose_name = 'Data Row'
        verbose_name_plural = 'Data Rows'
        default_related_name = 'field_data_row_set'

    id = models.AutoField(primary_key=True, db_column='field_data_row_id')
