from django.db import models
from django.core.validators import MaxValueValidator

from smartapi import base

class FieldSet(base.BaseTenantModel):
    class Meta:
        db_table = 'field_set'
        verbose_name = 'Fieldset'
        verbose_name_plural = 'Fieldsets'
        ordering = ['position']
        default_related_name = 'field_set_set'

    def __str__(self):
        return self.field_set_name

    id = models.AutoField(primary_key=True, db_column='field_set_id')
    module = models.CharField(max_length=200, blank=True, null=True)
    field_set_name = models.CharField(max_length=30, blank=True, null=True)
    system_flag = models.BooleanField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True, validators=[MaxValueValidator(99)])
    collapsed = models.BooleanField()
