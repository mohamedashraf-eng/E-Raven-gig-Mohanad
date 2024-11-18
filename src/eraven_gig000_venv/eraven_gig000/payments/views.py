# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from orders.models import Order
from .models import Payment
from ums.decorators import custom_login_required
from .gateways.base import PaymentGateway
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import uuid  # Ensure UUID is imported if needed

@custom_login_required
def select_payment_method(request, order_id):
    # Validate UUID format
    try:
        order_uuid = uuid.UUID(str(order_id))
    except ValueError:
        return HttpResponse('Invalid Order ID', status=400)

    order = get_object_or_404(Order, id=order_uuid, user=request.user)
    available_gateways = Payment.GATEWAY_CHOICES

    # Check if a payment already exists for this order
    existing_payment = Payment.objects.filter(order=order).first()
    if existing_payment:
        # Redirect to the existing payment's URL if it exists
        payment_url = existing_payment.get_payment_url()
        return redirect(payment_url)

    if request.method == 'POST':
        selected_gateway = request.POST.get('gateway')
        if selected_gateway not in dict(Payment.GATEWAY_CHOICES):
            # Handle invalid gateway selection
            return render(request, 'payments/select_payment_method.html', {
                'order': order,
                'available_gateways': available_gateways,
                'error': 'Invalid payment method selected.'
            })

        # Create Payment instance without setting payment_id
        payment = Payment.objects.create(
            order=order,
            gateway=selected_gateway,
            amount=order.get_total_cost(),
            currency='USD'  # You can make this dynamic as needed
        )

        try:
            # Redirect to the payment URL provided by the gateway
            payment_url = payment.get_payment_url()
            return redirect(payment_url)
        except Exception as e:
            # Handle gateway errors
            payment.delete()  # Optionally delete the payment if it failed
            return render(request, 'payments/select_payment_method.html', {
                'order': order,
                'available_gateways': available_gateways,
                'error': f'Payment gateway error: {str(e)}'
            })

    return render(request, 'payments/select_payment_method.html', {
        'order': order,
        'available_gateways': available_gateways
    })
    
def payment_success(request):
    # Render a success page
    return render(request, 'payments/payment_success.html')

def payment_cancel(request):
    # Render a cancellation page
    return render(request, 'payments/payment_cancel.html')

@csrf_exempt
def payment_webhook(request, gateway):
    try:
        gateway_class = PaymentGateway.get_gateway_class(gateway)
        gateway_instance = gateway_class()
        gateway_instance.process_response(request)
        return HttpResponse(status=200)
    except Exception as e:
        # Log the error
        return HttpResponse(status=400)
