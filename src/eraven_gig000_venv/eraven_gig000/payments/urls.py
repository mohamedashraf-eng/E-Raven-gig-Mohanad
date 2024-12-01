from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('select/<uuid:order_id>/', views.select_payment_method, name='select_payment_method'),
    path('paymob/response/', views.paymob_response, name='paymob_response'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]
