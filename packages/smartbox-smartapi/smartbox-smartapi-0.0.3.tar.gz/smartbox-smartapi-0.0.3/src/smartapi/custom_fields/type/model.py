from django.db import models

class FieldQuery(models.TextChoices):
    STRING = 'string', 'Text'
    ALPHA_NUM = 'alpha_num', 'Alpha Numeric'
    BOOLEAN = 'boolean', 'Checkbox'
    CURRENCY = 'currency', 'CURRENCY'
    PERCENTAGE = 'percentage', 'Percentage'
    DATE = 'date', 'Date'
    EMAIL = 'email', 'Email'
    NUMERIC = 'numeric', 'Number'
    PICKLIST = 'picklist', 'Pick List'
    CUSTOM = 'custom', 'Custom'
    RELATION = 'relation', 'Relation'
