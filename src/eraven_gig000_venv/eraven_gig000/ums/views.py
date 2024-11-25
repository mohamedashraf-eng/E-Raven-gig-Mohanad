# ums/views.py

from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile, Role, Permission
from .serializers import (
    UserSerializer, UserCreateSerializer, ProfileSerializer,
    RoleSerializer, PermissionSerializer, CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer
)
from .permissions import IsAdminOrReadOnly
from django.http import JsonResponse, HttpResponse, QueryDict
from datetime import timedelta
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
import logging
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from uuid import uuid4
from django.utils.encoding import force_str
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from cms.models import Enrollment, UserProgress, PointTransaction, Ranking, Course
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from .decorators import custom_login_required
from cms.models import Quiz, Assignment, Challenge, Course, Workshop, Article, Video, Assignment, Quiz, Challenge, Documentation, TimelineEvent, Submission
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .forms import UserProfileForm, UserSecurityForm

logger = logging.getLogger(__name__)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    Allows viewing, creating, and managing users.
    Admins can manage all users, while regular users can only view themselves.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        return UserCreateSerializer if self.action == 'create' else UserSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset  # Admins see all users
        return self.queryset.filter(id=self.request.user.id)  # Regular users see only their own details

class ProfileViewSet(viewsets.ModelViewSet):
    """
    Allows authenticated users to view and edit their own profile.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

class RoleViewSet(viewsets.ModelViewSet):
    """
    Restricted to admins, for creating and managing user roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]

class PermissionViewSet(viewsets.ModelViewSet):
    """
    Restricted to admins, for creating and managing permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Create a mutable copy of request.data
        data = request.data.copy()
        if isinstance(data, QueryDict):
            data = data.dict()

        password1 = data.get('password1')
        password2 = data.get('password2')

        if password1 != password2:
            return Response({"password2": ["Passwords do not match."]}, status=status.HTTP_400_BAD_REQUEST)

        # Add 'password' field with the value of password1 to satisfy serializer
        data['password'] = password1

        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            try:
                user = serializer.save()
            except IntegrityError as e:
                return Response({"detail": "Username or email already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a unique activation ID
            activation_id = str(uuid4())

            # Store user data in cache temporarily with the activation ID
            cache.set(f'activation_{activation_id}', serializer.validated_data, timeout=60 * 60 * 24)  # Expires in 24 hours
            cache.set(f'activation_email_{data["email"]}', activation_id, timeout=60 * 60 * 24)  # Map email to activation_id

            # Send activation email with the activation ID
            self.send_activation_email(activation_id, data['email'], data['username'], request)

            # Render the "check_email.html" page with the user's email
            return render(request, 'pages/check_email.html', {'user_email': data['email']})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_activation_email(self, activation_id, email, username, request):
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        activation_link = reverse('activate', kwargs={'activation_id': activation_id})
        activation_url = f"{request.scheme}://{current_site.domain}{activation_link}"

        context = {
            'activation_url': activation_url,
            'domain': current_site.domain,
            'username': username,
            'protocol': 'https' if request.is_secure() else 'http',
        }
        message = render_to_string('registration/activation_email.html', context)
        send_mail(
            subject=mail_subject,
            message=strip_tags(message),
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.debug(f"Resent activation email to {email}")

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, activation_id):
        # Retrieve user data from cache
        user_data = cache.get(f'activation_{activation_id}')
        if user_data:
            # Activate the user
            user = User.objects.get(email=user_data['email'])
            user.is_active = True
            user.save()
            
            # Clear the cached data after successful creation
            cache.delete(f'activation_{activation_id}')
            cache.delete(f'activation_email_{user_data["email"]}')
            
            # Render the success HTML page upon successful activation
            return render(request, 'registration/activate_account.html')
        else:
            # Activation link is invalid or expired
            return render(request, 'registration/activation_invalid.html', status=400)


class ResendActivationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve existing activation_id using email
        existing_activation_id = cache.get(f'activation_email_{email}')
        if existing_activation_id:
            user_data = cache.get(f'activation_{existing_activation_id}')
            if not user_data:
                # If user_data is missing, prompt re-registration
                return Response({"detail": "Activation data not found. Please register again."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If no activation_id exists, prompt re-registration
            return Response({"detail": "No pending activation found for this email. Please register."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new activation ID
        new_activation_id = str(uuid4())

        # Store user data in cache with the new activation ID
        cache.set(f'activation_{new_activation_id}', user_data, timeout=60 * 60 * 24)  # Expires in 24 hours
        cache.set(f'activation_email_{email}', new_activation_id, timeout=60 * 60 * 24)  # Map email to new activation_id

        # Send the new activation email
        self.send_activation_email(new_activation_id, email, user_data.get('username'), request)

        return Response({"detail": "Activation email resent. Please check your email."}, status=status.HTTP_200_OK)

    def send_activation_email(self, activation_id, email, username, request):
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        activation_link = reverse('activate', kwargs={'activation_id': activation_id})
        activation_url = f"{request.scheme}://{current_site.domain}{activation_link}"

        context = {
            'activation_url': activation_url,
            'domain': current_site.domain,
            'username': username,
            'protocol': 'https' if request.is_secure() else 'http',
        }
        message = render_to_string('registration/activation_email.html', context)
        send_mail(
            subject=mail_subject,
            message=strip_tags(message),
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.debug(f"Resent activation email to {email}")

def set_auth_cookies(response, access_token=None, refresh_token=None):
    """Helper function to set access and refresh tokens as cookies."""
    if access_token:
        response.set_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE'],
            access_token,
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )
    if refresh_token:
        response.set_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            refresh_token,
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )
    return response

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining tokens and setting them in cookies.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh = RefreshToken(response.data['refresh'])
            response = set_auth_cookies(
                response,
                access_token=str(refresh.access_token),
                refresh_token=str(refresh),
            )
            # Remove tokens from response data to avoid redundant transfer
            response.data.pop('access', None)
            response.data.pop('refresh', None)
        return response

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing access tokens using the refresh token from cookies.
    """
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Access token was refreshed successfully
            access_token = response.data.get('access')

            # Set the new access token in the cookie
            response = set_auth_cookies(response, access_token=access_token)

            # Remove the access token from the response body to avoid redundancy
            response.data.pop('access', None)
        else:
            # Refresh failed: possible invalid or expired refresh token
            # Optionally, clear the refresh token cookie
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            response = redirect('sign-in')  # Redirect to sign-in page
            return response

        return response

from django.http import HttpResponseRedirect
class LogoutView(APIView):
    """
    Logs out the user by deleting the authentication cookies.
    """
    permission_classes = [IsAuthenticated]

    def _delete_auth_cookies(self, response):
        """
        Helper method to delete authentication cookies.
        """
        response.delete_cookie(
            key=settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token')
        )
        response.delete_cookie(
            key=settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')
        )
        return response

    def get(self, request, *args, **kwargs):
        response = HttpResponseRedirect(reverse('landing-page'))
        return self._delete_auth_cookies(response)

    def post(self, request, *args, **kwargs):
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        return self._delete_auth_cookies(response)

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        
        try:
            # Verify if a user exists with the provided email
            user = User.objects.get(email=email)
            logger.debug(f"User found with email {email}")

            # Generate the UID and token for the reset URL
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Construct the password reset URL
            reset_url = self.request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Prepare the email context
            subject = "Password Reset Requested"
            context = {
                'user': user,
                'reset_url': reset_url,
                'domain': self.request.get_host(),
                'protocol': 'https' if self.request.is_secure() else 'http',
            }

            # Render HTML message and plain text fallback
            html_message = render_to_string('registration/password_reset_email.html', context)
            plain_message = strip_tags(html_message)  # Plain text fallback

            # Send the email with HTML content only
            send_mail(
                subject=subject,
                message=plain_message,  # Plain text version
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,  # HTML version
                fail_silently=False,
            )
            logger.debug(f"Password reset email sent successfully to {email}")

            # Redirect to password_reset_done page after successful email
            return redirect(reverse('password_reset_done'))

        except User.DoesNotExist:
            logger.warning(f"No user found with email {email}")
            form.add_error('email', "No account found with this email address.")
            return self.form_invalid(form)
    
def token_lifetime_view(request):
    access_token_lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=15)).total_seconds()
    return JsonResponse({'access_token_lifetime': access_token_lifetime})

@method_decorator(custom_login_required, name='dispatch')
class UserProfileView(View):
    """
    Displays the authenticated user's profile, including courses, progress, points, and timeline events.
    """

    def get_submission_count(self, user, model):
        """
        Helper method to count submissions for a specific content type.
        """
        try:
            ct = ContentType.objects.get_for_model(model)
            return Submission.objects.filter(user=user, content_type=ct).count()
        except ContentType.DoesNotExist:
            logger.error(f"ContentType for model {model.__name__} does not exist.")
            return 0

    def get_accessible_courses(self, user):
        """
        Retrieves all courses the user can access via enrollments or purchased bundles.
        """
        # Courses via explicit enrollments
        enrolled_courses = set(
            Enrollment.objects.filter(user=user).values_list('course_id', flat=True)
        )

        # Courses via purchased bundles
        bundle_courses = set(
            Course.objects.filter(products__users=user).values_list('id', flat=True)
        )

        # Combine both sets
        accessible_course_ids = enrolled_courses.union(bundle_courses)

        # Retrieve all accessible courses
        return Course.objects.filter(id__in=accessible_course_ids)

    def ensure_enrollments(self, user, courses):
        """
        Ensures that an Enrollment exists for all accessible courses.
        """
        existing_enrollments = Enrollment.objects.filter(user=user, course__in=courses)
        existing_course_ids = set(existing_enrollments.values_list('course_id', flat=True))

        # Find courses without enrollments
        unenrolled_courses = [course for course in courses if course.id not in existing_course_ids]

        # Bulk create enrollments for unenrolled courses
        Enrollment.objects.bulk_create(
            [Enrollment(user=user, course=course) for course in unenrolled_courses]
        )

    def create_user_progress_for_enrollments(self, user, enrollments):
        """
        Ensures that a UserProgress entry exists for each enrollment.
        """
        for enrollment in enrollments:
            # Check if UserProgress already exists for this user and course
            UserProgress.objects.get_or_create(
                user=user,
                course=enrollment.course,
                progress_percentage=0.0,  # Default progress
                completed=False            # Default not completed
            )

    def get(self, request, *args, **kwargs):
        user = request.user

        # **1. Dashboard Counts**
        quiz_count = self.get_submission_count(user, Quiz)
        assignment_count = self.get_submission_count(user, Assignment)
        challenge_count = self.get_submission_count(user, Challenge)
        workshop_count = self.get_submission_count(user, Workshop)

        # **2. Accessible Courses**
        accessible_courses = self.get_accessible_courses(user)

        # **3. Ensure Enrollments**
        self.ensure_enrollments(user, accessible_courses)

        # **4. Create UserProgress for each Enrollment**
        enrollments = Enrollment.objects.filter(user=user)
        self.create_user_progress_for_enrollments(user, enrollments)

        # **5. Progress**
        progresses = UserProgress.objects.filter(user=user).select_related('course')

        # **6. Points and Ranking**
        ranking = Ranking.objects.filter(user=user).first()
        point_transactions = PointTransaction.objects.filter(user=user).order_by('-timestamp')[:10]  # Latest 10 transactions

        # **7. Global Rankings**
        top_rankings = Ranking.objects.order_by('-points')[:10]  # Top 10 users

        # **8. Timeline Events**
        timeline_events = TimelineEvent.objects.filter(
            user=user,
            event_date__gte=timezone.now()
        ).order_by('event_date')

        # **9. Validate Timeline Events**
        valid_timeline_events = []
        for event in timeline_events:
            try:
                obj = event.content_object
                valid_timeline_events.append(event)
            except Exception as e:
                logger.error(f"Faulty TimelineEvent ID: {event.id}, Error: {e}")
                
        enrollments = {enrollment.course_id: enrollment for enrollment in Enrollment.objects.filter(user=user)}
        
        # **10. Context Dictionary**
        context = {
            'quiz_count': quiz_count,
            'assignment_count': assignment_count,
            'challenge_count': challenge_count,
            'workshop_count': workshop_count,
            'courses': accessible_courses,  # Accessible courses (from enrollments and bundles)
            'enrollments': enrollments,     # Dictionary of enrollments for quick lookup
            'progresses': progresses,
            'ranking': ranking,
            'point_transactions': point_transactions,
            'rankings': top_rankings,
            'timeline_events': valid_timeline_events,
        }

        return render(request, 'cms/user_profile.html', context)
    
class UserProfileEditView(LoginRequiredMixin, View):
    template_name = 'cms/user_profile_edit.html'

    def get(self, request, *args, **kwargs):
        profile_form = UserProfileForm(instance=request.user)
        security_form = UserSecurityForm(user=request.user)
        return render(request, self.template_name, {
            'profile_form': profile_form,
            'security_form': security_form,
        })

    def post(self, request, *args, **kwargs):
        if 'save_changes' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            security_form = UserSecurityForm(user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('user_profile')
            else:
                messages.error(request, 'Please correct the errors below in your personal data.')
        elif 'update_password' in request.POST:
            profile_form = UserProfileForm(instance=request.user)
            security_form = UserSecurityForm(request.POST, user=request.user)
            if security_form.is_valid():
                security_form.save()
                messages.success(request, 'Your password has been updated successfully.')
                return redirect('user_profile')
            else:
                messages.error(request, 'Please correct the errors below in your security settings.')
        else:
            profile_form = UserProfileForm(instance=request.user)
            security_form = UserSecurityForm(user=request.user)
            messages.error(request, 'Invalid form submission.')

        return render(request, self.template_name, {
            'profile_form': profile_form,
            'security_form': security_form,
        })