# ums/middleware.py

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
