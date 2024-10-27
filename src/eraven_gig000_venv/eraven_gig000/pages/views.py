# pages/views.py
from django.conf.urls import handler404, handler500, handler403
from django.shortcuts import render

def landing_page_view(request):
    return render(request, 'pages/index.html')

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