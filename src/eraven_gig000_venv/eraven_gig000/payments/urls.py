from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('select/<uuid:order_id>/', views.select_payment_method, name='select_payment_method'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/<str:gateway>/', views.payment_webhook, name='payment_webhook'),  # For handling webhooks
]
