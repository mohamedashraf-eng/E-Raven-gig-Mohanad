# ums/decorators.py

from django.shortcuts import redirect
from django.urls import reverse_lazy
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verify user authentication
        if not request.user.is_authenticated:
            # Log unauthorized access attempt
            logger.warning(f"Unauthorized access attempt to {request.path} by an anonymous user.")

            # Only perform redirection if the request is a GET method
            if request.method == 'GET':
                # Redirect to a safe, dynamically resolved login URL
                return redirect(reverse_lazy('sign-in'))

            # For non-GET methods, return an HTTP 401 Unauthorized response
            from django.http import HttpResponse
            return HttpResponse('Unauthorized', status=401)
        
        # Proceed with the view function if user is authenticated
        return view_func(request, *args, **kwargs)

    return _wrapped_view
