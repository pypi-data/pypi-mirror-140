import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

import jwt
from jwt import DecodeError

from pfx.pfxcore.exceptions import APIError, AuthenticationError
from pfx.pfxcore.models import CacheableMixin

logger = logging.getLogger(__name__)


class JWTTokenDecodeMixin:

    @classmethod
    def get_cached_user(cls, pk):
        UserModel = get_user_model()
        has_cache = issubclass(UserModel, CacheableMixin)
        if (has_cache):   # pragma: no cover
            user = UserModel.cache_get(pk)
            if user:
                return user
        user = UserModel._default_manager.get(pk=pk)
        if (has_cache):   # pragma: no cover
            user.cache()
        return user

    @classmethod
    def decode_jwt(cls, token):
        try:
            opts = ({"require": ["exp"]} if settings.PFX_TOKEN_VALIDITY
                    else {})
            decoded = jwt.decode(
                token, settings.PFX_SECRET_KEY,
                options=opts,
                algorithms="HS256")
            return cls.get_cached_user(decoded['pfx_user_pk'])
        except DecodeError as e:
            logger.exception(e)
            raise AuthenticationError(message=_('Authentication error'))
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(message=_('Token has expired'))
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise AuthenticationError(message=_('Authentication error'),
                                      status=500)


class AuthenticationMiddleware(JWTTokenDecodeMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authorization = request.headers.get('Authorization')
        if authorization:
            try:
                _, key = authorization.split("Bearer ")
            except ValueError:  # pragma: no cover
                key = None
            try:
                request.user = self.decode_jwt(key)
            except get_user_model().DoesNotExist:   # pragma: no cover
                return JsonResponse(
                    {'message': _("Authentication error")}, status=401)
            except APIError as e:
                return e.response
        else:
            if not hasattr(request, 'user'):
                request.user = AnonymousUser()

        return self.get_response(request)


class CookieAuthenticationMiddleware(JWTTokenDecodeMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        key = request.COOKIES.get('token')
        if key:
            try:
                request.user = self.decode_jwt(key)
            except get_user_model().DoesNotExist:   # pragma: no cover
                return JsonResponse(
                    {'message': 'Authentication error'}, status=401)
            except APIError as e:
                return e.response
        else:
            if not hasattr(request, 'user'):   # pragma: no cover
                request.user = AnonymousUser()
        return self.get_response(request)
