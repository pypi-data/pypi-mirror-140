import graphene

from django.db import models
from graphene import String
from graphene_django_cud.converter import convert_django_field_to_input
from graphene_django.converter import convert_django_field
from django.core.validators import MaxLengthValidator

class CurrencyField(models.DecimalField):

    description = "A currency field"



class PhoneField(models.Field):

    description = "A phone number"

    def __init__(self, max_length=20, validators=[], *args, **kwargs):
        self.max_length = max_length
        self.validators = validators

        self.validators.append(MaxLengthValidator(self.max_length))
        super().__init__(*args, **kwargs)

class FaxField(models.Field):

    description = "A fax number"

    def __init__(self, max_length=20, validators=[], *args, **kwargs):
        self.max_length = max_length
        self.validators = validators

        self.validators.append(MaxLengthValidator(self.max_length))
        super().__init__(*args, **kwargs)

@convert_django_field_to_input.register(PhoneField)
@convert_django_field_to_input.register(FaxField)
def convert_to_string_extended(field,registry=None,required=None,field_many_to_many_extras=None,field_foreign_key_extras=None,field_one_to_one_extras=None,):
    return String(description=field.help_text, required= not field.null)

@convert_django_field.register(PhoneField)
@convert_django_field.register(FaxField)
def convert_field_to_string(field, registry=None):
    return graphene.String()
