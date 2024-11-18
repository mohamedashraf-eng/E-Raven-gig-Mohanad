# payments/gateways/stripe.py

import stripe
from django.conf import settings
from django.urls import reverse
from payments.gateways.base import PaymentGateway
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeGateway(PaymentGateway):
    def get_payment_url(self, payment: Payment) -> str:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': payment.currency.lower(),
                    'product_data': {
                        'name': f'Order {payment.order.id}',
                    },
                    'unit_amount': int(payment.amount * 100),  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.SITE_URL + reverse('payments:payment_success'),
            cancel_url=settings.SITE_URL + reverse('payments:payment_cancel'),
            metadata={'payment_id': str(payment.id)},  # Store UUID as string
        )
        # Set the payment_id to the Stripe session ID (unique)
        payment.payment_id = session.id
        payment.save()
        return session.url

    def process_response(self, request) -> None:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            # Invalid payload
            return
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            payment_id = session['metadata']['payment_id']
            try:
                payment = Payment.objects.get(id=payment_id)
                payment.status = 'completed'
                payment.save()
            except Payment.DoesNotExist:
                # Handle missing payment
                pass
        # ... handle other event types as needed
