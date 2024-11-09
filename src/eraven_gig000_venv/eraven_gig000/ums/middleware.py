# ums/middleware.py

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate users based on JWT tokens stored in cookies.
    Redirects to a custom endpoint if the token is expired.
    """

    def process_request(self, request):
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if access_token:
            try:
                # Decode the JWT token
                payload = jwt.decode(
                    access_token,
                    settings.SIMPLE_JWT['SIGNING_KEY'],
                    algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
                )
                user_id = payload.get('user_id')

                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                        logger.debug(f"Authenticated user: {user.username}")
                    except User.DoesNotExist:
                        request.user = AnonymousUser()
                        logger.warning(f"User with ID {user_id} does not exist.")
                else:
                    request.user = AnonymousUser()
                    logger.warning("JWT token does not contain user_id.")
            except jwt.ExpiredSignatureError:
                # Token has expired
                request.user = AnonymousUser()
                logger.warning("JWT token has expired.")
                # Redirect to custom endpoint
                if not request.path.startswith('/api/v1/pages/sign-in'):
                    return redirect('/api/v1/pages/sign-in')
            except jwt.InvalidTokenError:
                # Invalid token
                request.user = AnonymousUser()
                logger.warning("Invalid JWT token.")
        else:
            request.user = AnonymousUser()
            logger.debug("No JWT access token found in cookies.")
