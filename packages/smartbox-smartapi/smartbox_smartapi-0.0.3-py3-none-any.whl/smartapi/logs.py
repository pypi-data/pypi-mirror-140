import logging
import os
from django.conf import settings
from django.http import JsonResponse
from itertools import islice
from graphene_file_upload.django import FileUploadGraphQLView
from graphql.error import format_error as format_graphql_error
from graphql.error import GraphQLError
import logging
import pprint
import re
from django.contrib.auth.decorators import user_passes_test

from .decorators import set_jwt_cookie, superuser_required_401

import json

import traceback

# Get an instance of a logger
logger = logging.getLogger("api")
logger_graphql = logging.getLogger("graphql")

def debug(message, data = None, request = {}):
    logger = logging.getLogger("api")
    logger.debug(message, extra={"debug": data, "request": request})

class LoggerGraphQLView(FileUploadGraphQLView):
    graphiql = settings.DEBUG

    def format_error(self, error):
        try:
            if(error.original_error.__class__.__name__ == "JSONWebTokenError"):
                return {"message": 'UnauthorizedError'}
        except AttributeError:
            try:
                if(error.__class__.__name__ == "JSONWebTokenError"):
                    return {"message": 'UnauthorizedError'}
            except:
                pass

        if isinstance(error, GraphQLError):
            return format_graphql_error(error)

        return {"message": str(error)}

    def parse_body(self, request):

        # Allow for variable batch
        try:
            body = request.body.decode("utf-8")
            request_json = json.loads(body)
            self.batch = isinstance(request_json, list)
        except:
            self.batch = False
        return super().parse_body(request)

    def execute_graphql_request(self, request, data, query, variables, operation_name, show_graphiql):

        """Log Errors"""
        result = super().execute_graphql_request(request, data, query, variables, operation_name, show_graphiql)
        logger_graphql.info(operation_name, extra={'request_info': [ query, variables], 'request': self.get_context(request)})

        if result.errors:
            self._capture_exceptions(result.errors, [query, variables], request)

        return result

    def _capture_exceptions(self, errors, args, request):
        for error in errors:

            stack = []
            try:
                stack = traceback.format_tb(error.stack)[::-1]
            except AttributeError as e:
                stack = traceback.format_tb(e.__traceback__)[::-1]

            try:
                if(error.original_error.__class__.__name__ != "FriendlyError"):
                    logger.error(str(error.original_error), stack_info=False, extra={'stack': '\\n'.join(stack), 'request_info': args, 'request': self.get_context(request)})
            except AttributeError:
                if(error.__class__.__name__ != "FriendlyError"):
                    logger.error(str(error), stack_info=False, extra={'stack': '\\n'.join(stack), 'request_info': args, 'request': self.get_context(request)})


class InfoLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO

class DebugLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG

class ErrorLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.ERROR or record.levelno == logging.WARNING or record.levelno == logging.CRITICAL

class AddContextToLogFilter(logging.Filter):
    def filter(self, record):
        record.comp = 'n/a'
        record.user = 'n/a'
        if(not hasattr(record, 'request_info')):
            record.request_info = ''

        #todo: figure ou why sometimes the user is anonymous
        if hasattr(record, 'request') and hasattr(record.request, 'user'):
            record.user = record.request.user.username
            if hasattr(record.request.user, 'comp'):
                record.comp = record.request.user.comp.comp_id

        if(not hasattr(record, 'debug')):
            record.debug = ''

        return True


def get_logs(qfile, offset, limit, search = {}):
    lines = qfile.readlines()
    logs = []
    concat = ''
    count = 0
    matched = True
    for line in reversed(lines):
        if line.startswith('[ERROR]') or line.startswith('[INFO]') or line.startswith('[DEBUG]') or line.startswith('[CRITICAL]') or line.startswith('[WARNING]'):
            concat = line+concat

            if 'long_query' in search and search['long_query']:
                matched = False
                parts = re.split("Duration:\s([0-9.]*)\sseconds$", concat, re.MULTILINE)

                if len(parts) > 1:
                    if float(parts[1]) > float(search['long_query']):
                        print('matched')
                        matched = True
            elif 'match' in search and search['match']:
                matched = re.search(search['match'], concat, re.MULTILINE)
            else:
                matched = True

            if matched:
                count += 1
                if count > offset:
                    logs.append(concat)

                if count >= limit+offset:
                    break

            concat = ''
        else:
            concat = line+concat

    return logs

@set_jwt_cookie
@superuser_required_401
def show_log_file(args):

    lines_per_page = 20

    file_name = args.GET.get('type', 'debug')+'.log'
    page = int(args.GET.get('page', 1))

    search = json.loads(args.GET.get('search', '{}'))

    context = {}

    if file_name:
        file_log = os.path.join(settings.LOG_VIEWER_FILES_DIR, file_name)
        with open(file_log, encoding='utf8', errors='ignore') as file:
            next_lines = list(get_logs(file, (page - 1) * lines_per_page, lines_per_page, search))

            if len(next_lines) < lines_per_page:
                context['last'] = True
            else:
                context['last'] = False
            context['logs'] = next_lines[0:lines_per_page]
    else:
        context['last'] = True

    return JsonResponse(context)
