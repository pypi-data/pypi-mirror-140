# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from smartapi import base

from .set.model import FieldSet

class Field(base.BaseTenantModel):
    class Meta:
        db_table = 'field'
        verbose_name = 'Field'
        verbose_name_plural = 'Fields'
        ordering = ['row_no', 'column_no']
        unique_together = (('comp', 'identifier', 'module'),)
        default_related_name = 'field_set'

    def __str__(self):
        return self.field_name

    id = models.AutoField(primary_key=True, db_column='field_id')

    field_set = models.ForeignKey(
        FieldSet,
        verbose_name='Fieldset',
        on_delete=models.CASCADE
    )

    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20)
    mandatory_flag = models.BooleanField()
    field_length = models.IntegerField(blank=True, null=True)
    #summary_view_flag = models.BooleanField()
    column_no = models.IntegerField()
    row_no = models.IntegerField()
    active_flag = models.BooleanField()
    default_value = models.CharField(max_length=2000, blank=True, null=True)
    db_column = models.CharField(max_length=2000, blank=True, null=True)
    decimals = models.IntegerField(blank=True, null=True)
    picklist_source = models.TextField(blank=True, null=True)
    relation_module = models.CharField(max_length=500, blank=True, null=True)
    internal_desc = models.CharField(max_length=4000, blank=True, null=True)
    identifier = models.CharField(max_length=100)
    module = models.CharField(max_length=200)
    regex = models.CharField(max_length=200, blank=True, null=True)
