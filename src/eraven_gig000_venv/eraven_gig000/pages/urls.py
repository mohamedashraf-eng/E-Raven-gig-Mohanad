# pages/urls.py

from django.urls import path
from .views import (
    SignInView, SignUpView, LogoutView,
    landing_page_view, about_view, contact_view,
    terms_view, policy_view, payment_policy_view,
    refund_policy_view, privacy_policy_view, info_view
)

urlpatterns = [
    path('', landing_page_view, name='landing-page'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('terms/', terms_view, name='terms'),
    path('policy/', policy_view, name='policy'),
    path('payment-policy/', payment_policy_view, name='payment-policy'),
    path('refund-policy/', refund_policy_view, name='refund-policy'),
    path('privacy-policy/', privacy_policy_view, name='privacy-policy'),
    path('info/', info_view, name='info'),
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
