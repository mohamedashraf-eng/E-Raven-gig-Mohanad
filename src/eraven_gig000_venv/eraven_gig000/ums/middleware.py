# ums/middleware.py

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.urls import reverse
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
        # List of paths to exclude from authentication
        excluded_paths = [
            reverse('sign-in'),  # Adjust 'pages:sign_in' to your sign-in URL name
            reverse('sign-up'),  # If you have a sign-up page
        ]

        # Allow access to excluded paths without authentication
        if request.path in excluded_paths:
            request.user = AnonymousUser()
            return

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
                return redirect(reverse('sign-in'))
            except jwt.InvalidTokenError:
                # Invalid token
                request.user = AnonymousUser()
                logger.warning("Invalid JWT token.")
        else:
            request.user = AnonymousUser()
            logger.debug("No JWT access token found in cookies.")
