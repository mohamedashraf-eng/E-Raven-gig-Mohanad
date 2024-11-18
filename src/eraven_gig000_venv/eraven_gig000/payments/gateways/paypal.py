# payments/gateways/paypal.py

import paypalrestsdk
from django.conf import settings
from django.urls import reverse
from payments.gateways.base import PaymentGateway
from payments.models import Payment

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" in production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

class PayPalGateway(PaymentGateway):
    def get_payment_url(self, payment: Payment) -> str:
        payment_obj = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": settings.SITE_URL + reverse('payments:payment_success'),
                "cancel_url": settings.SITE_URL + reverse('payments:payment_cancel'),
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Order {payment.order.id}",
                        "sku": f"order_{payment.order.id}",
                        "price": f"{payment.amount}",
                        "currency": payment.currency,
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{payment.amount}",
                    "currency": payment.currency
                },
                "description": f"Payment for Order {payment.order.id}"
            }]
        })

        if payment_obj.create():
            for link in payment_obj.links:
                if link.rel == "approval_url":
                    # Set the payment_id to the PayPal payment ID
                    payment.payment_id = payment_obj.id
                    payment.save()
                    return str(link.href)
        else:
            # Handle payment creation failure
            raise Exception(payment_obj.error)

    def process_response(self, request) -> None:
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        payment_obj = paypalrestsdk.Payment.find(payment_id)

        if payment_obj.execute({"payer_id": payer_id}):
            try:
                payment_record = Payment.objects.get(payment_id=payment_obj.id)
                payment_record.status = 'completed'
                payment_record.save()
            except Payment.DoesNotExist:
                # Handle missing payment
                pass
        else:
            try:
                payment_record = Payment.objects.get(payment_id=payment_obj.id)
                payment_record.status = 'failed'
                payment_record.save()
            except Payment.DoesNotExist:
                # Handle missing payment
                pass
