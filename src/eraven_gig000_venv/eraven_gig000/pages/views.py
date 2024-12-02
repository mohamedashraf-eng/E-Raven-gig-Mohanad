# pages/views.py
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib import messages
import logging
from django.urls import reverse
from cms.models import Enrollment
from products.models import Product
from ums.decorators import custom_login_required
import requests  # Ensure requests is imported


# Configure logging
logger = logging.getLogger(__name__)

def landing_page_view(request):
    products = Product.objects.filter(available=True)  # Fetching available products
    return render(request, 'pages/index.html', {'products': products})

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

def terms_view(request):
    return render(request, 'pages/terms.html')

def policy_view(request):
    return render(request, 'pages/policy.html')

def payment_policy_view(request):
    return render(request, 'pages/payment_policy.html')

def refund_policy_view(request):
    return render(request, 'pages/refund_policy.html')

def privacy_policy_view(request):
    return render(request, 'pages/privacy.html')

def info_view(request):
    return render(request, 'pages/info.html')

class SignInView(View):
    def get(self, request):
        return render(request, 'pages/sign_in.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            response = redirect('landing-page')  # Change to your desired redirect URL
            # Set the access token in a cookie
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'],
                str(refresh.access_token),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            )
            # Set the refresh token in a cookie
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                str(refresh),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            )
            messages.success(request, 'Welcome back! You are now signed in.')
            logger.info(f"User '{username}' signed in successfully.")
            return response
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            logger.warning(f"Failed sign-in attempt for username: '{username}'.")
            return render(request, 'pages/sign_in.html', {'error': 'Invalid username or password'})

class SignUpView(View):
    """
    Handles user registration by sending user data to the ums API
    and redirecting to the sign-in page upon successful registration.
    """

    def get(self, request):
        return render(request, 'pages/sign_up.html')

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match. Please try again.")
            logger.warning(f"Password mismatch during registration for username: '{username}'.")
            return render(request, 'pages/sign_up.html', {'error': 'Passwords do not match.'})

        # Additional validation (e.g., password strength, email format) can be added here

        # Prepare payload for ums API
        payload = {
            'username': username,
            'email': email,
            'password1': password1,
            'password2': password2,
        }

        try:
            # Send a POST request to the ums API to create a new user
            api_url = request.build_absolute_uri(reverse('user-registration')) 
            response = requests.post(
                api_url,
                json=payload,
                cookies=request.COOKIES
            )
            response_data = response.json()

            if response.status_code == 201:
                logger.info(f"User '{username}' registered successfully.")
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
                return redirect('sign-in')
            else:
                logger.warning(f"Sign-up failed for user '{username}': {response_data}")
                error_message = response_data.get('detail', 'Registration failed. Please try again.')
                messages.error(request, error_message)
                return render(request, 'pages/sign_up.html', {'error': error_message})

        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to ums API during sign-up for user '{username}': {e}")
            messages.error(request, 'Unable to connect to the registration server. Please try again later.')
            return render(request, 'pages/sign_up.html', {'error': 'Unable to connect to registration server.'})

class LogoutView(View):
    """
    Handles user logout by clearing JWT tokens from cookies
    and redirecting to the landing page.
    """

    def get(self, request):
        response = redirect('landing-page')  # Change to your desired redirect URL

        # Delete the access token cookie
        response.delete_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE'],
            path='/',
        )

        # Delete the refresh token cookie
        response.delete_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            path='/',
        )

        messages.success(request, 'You have been logged out successfully.')
        logger.info(f"User '{request.user}' logged out successfully.")
        return response

def check_email(request):
    # Optionally, retrieve the user's email from the session or pass it via query parameters
    user_email = request.GET.get('email', '')
    messages.info(request, 'Please check your email for a verification link.')
    logger.info(f"User '{request.user}' prompted to check email: '{user_email}'.")
    return render(request, 'pages/check_email.html', {'user_email': user_email})

@custom_login_required
def enrolled_courses_view(request):
    user = request.user
    # Retrieve all enrollment instances for the current user
    enrollments = Enrollment.objects.filter(user=user).select_related('course')
    # Extract the courses from the enrollments
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    
    if not enrolled_courses:
        messages.info(request, 'You are not enrolled in any courses yet. Explore our courses to get started.')

    context = {
        'enrolled_courses': enrolled_courses
    }
    return render(request, 'pages/enrolled_courses.html', context)
