from graphene.utils.str_converters import to_camel_case
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.conf import settings
from django.utils.module_loading import import_string
Comp = import_string(settings.TENANT_MODEL)

from . import errors

from graphql import GraphQLError

def get_comp(request, kwargs = {}):
    if request.user and not request.user.is_anonymous:
        return request.user.comp
    else:
        subdomain = None
        if 'subdomain' in request.resolver_match.kwargs:
            subdomain = request.resolver_match.kwargs['subdomain']
        elif 'publickey' in kwargs:
            subdomain = kwargs['publickey']

        comps = Comp.objects.raw('SELECT * FROM '+settings.ADMIN_DB_USERNAME+'.'+Comp._meta.db_table+' where subdomain = %s', [subdomain])

        if len(comps) == 0:
            raise errors.GraphQLError('Invalid subdomain')

        return comps[0]


def csrf(request):
    #token = get_token(request)
    return JsonResponse({'ok': True})

def generate_translation(args):
    Query = import_string(settings.SCHEMA+'.Query')

    import django
    from django.apps import apps
    from django.http import JsonResponse


    import pprint
    import re

    to_snake_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    translations = {}
    for model in apps.get_app_config('api').get_models():
        model_name = to_snake_case_pattern.sub('_', model.__name__).lower()
        translations[model_name] = {}
        translations[model_name]['name'] = str(getattr(model._meta, 'verbose_name', None))+' | '+str(getattr(model._meta, 'verbose_name_plural', None))

        if(getattr(model._meta, 'help', None)):
            translations[model_name]['help'] = getattr(model._meta, 'help', None)

        translations[model_name]['fields'] = {}

        for field in model._meta.get_fields():
            if field.name != 'comp' and getattr(field, 'verbose_name', None):
                translations[model_name]['fields'][field.name] = {
                    'name':  getattr(field, 'verbose_name', None),
                }
                if(getattr(field, 'help', None)):
                    translations[model_name]['fields'][field.name]['help'] =  getattr(field, 'help', None)


                choices = getattr(field, 'choices', None)

                if choices :
                    choices = list(choices)
                    translations[model_name]['fields'][field.name]['choices'] = {}
                    for x in range(len(choices)):
                        choices[x] = list(choices[x])
                        if isinstance(choices[x][0], int):
                            choices[x][0] = 'A_'+str(choices[x][0])
                        translations[model_name]['fields'][field.name]['choices'][choices[x][0]] = choices[x][1]

    return JsonResponse(translations)

def generate_definition(args):

    #todo call all imports somewhere, why __init__.py doesn't work? :( I guess importing the enire graphql schema is ok
    Query = import_string(settings.SCHEMA+'.Query')

    import django
    from django.apps import apps
    from django.http import JsonResponse

    import pprint
    import re

    to_snake_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    definition = {}
    for model in apps.get_app_config('api').get_models():
        model_name = to_snake_case_pattern.sub('_', model.__name__).lower()
        definition[model_name] = {}
        definition[model_name]['model'] = model_name
        definition[model_name]['ordering'] = getattr(model._meta, 'ordering', None)

        if(getattr(model._meta, 'indexes', None)):
            definition[model_name]['indexes'] = []
            for index in getattr(model._meta, 'indexes'):
                definition[model_name]['indexes'].append(index.fields)

        definition[model_name]['fields'] = {}

        for field in model._meta.get_fields():
            if field.name != 'comp':
                definition[model_name]['fields'][field.name] = {
                    'primary_key': getattr(field, 'primary_key', False),
                    'default': None if not hasattr(field, 'default') or hasattr(field.default, '__name__') else field.default,
                    'generated_default': True if hasattr(field, 'default') and hasattr(field.default, '__name__') and field.default.__name__ != 'NOT_PROVIDED' else False,
                    'type': field.__class__.__name__,
                    'max_length': getattr(field, 'max_length', None),
                    'blank': getattr(field, 'blank', False),
                    'editable': getattr(field, 'editable', True),
                    #really ugly to debug stuff, but that's the best i could do :
                    #'exra': pprint.pformat(getattr(field, 'validators', None)),
                }

                if definition[model_name]['fields'][field.name]['type'] == 'FileField' and getattr(field, 'validators', None):
                    definition[model_name]['fields'][field.name]['exts'] = list(field.validators[0].content_types.keys())

                choices = getattr(field, 'choices', None)

                integer_choice = False
                if choices :
                    definition[model_name]['fields'][field.name]['choices_debug'] = choices
                    choices = list(choices)
                    for x in range(len(choices)):
                        choices[x] = list(choices[x])
                        if isinstance(choices[x][0], int):
                            choices[x][0] = 'A_'+str(choices[x][0])
                            integer_choice = True
                    definition[model_name]['fields'][field.name]['choices'] = choices

                if integer_choice and definition[model_name]['fields'][field.name]['default']:
                    definition[model_name]['fields'][field.name]['default'] =  'A_'+str(definition[model_name]['fields'][field.name]['default'])

                if hasattr(field, 'foreign_related_fields') :
                    foreign_field = field.foreign_related_fields[0]

                    definition[model_name]['fields'][field.name]['has_one'] = {
                        'model':to_snake_case_pattern.sub('_', foreign_field.model.__name__).lower(),
                        'field':foreign_field.name,
                        #really ugly to debug stuff, but that's the best i could do :
                        #'exra': pprint.pformat(vars(foreign_field)),
                    }
                elif hasattr(field.related_model, '__name__') :

                    #foreign_field = field.related_fields[0]
                    definition[model_name]['fields'][field.name]['belongs_to'] = {
                        'model': to_snake_case_pattern.sub('_', getattr(field.related_model, '__name__', None)).lower(),
                        #'exra': pprint.pformat(vars(field)),
                    }


    return JsonResponse(definition)
