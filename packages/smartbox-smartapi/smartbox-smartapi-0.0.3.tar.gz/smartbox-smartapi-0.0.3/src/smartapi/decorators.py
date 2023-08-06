from functools import wraps
from graphql_jwt.settings import jwt_settings
from graphql_jwt.shortcuts import get_user_by_token
from django.http import HttpResponse, Http404

def user_passes_test(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return HttpResponse('Unauthorized', status=401)
        return _wrapped_view
    return decorator


def login_required_401(function=None):

    actual_decorator = user_passes_test(
        lambda u: u and u.is_authenticated,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def superuser_required_401(function=None):
    actual_decorator = user_passes_test(
        lambda u: u and u.is_superuser,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def not_found():
    response = HttpResponse("", content_type='application/html')
    response['Content-Disposition'] = 'attachment; filename=notfound.html'
    return response

def not_found_on_error(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    try:
        return function(request, *args, **kwargs)
    except:
        return not_found()
  return wrap


def set_jwt_cookie(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    token = request.COOKIES.get(jwt_settings.JWT_COOKIE_NAME)
    if token:
        request.user = get_user_by_token(token, request)
    return function(request, *args, **kwargs)

  return wrap
