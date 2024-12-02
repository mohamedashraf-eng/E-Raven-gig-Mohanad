import requests
from django.conf import settings
from django.urls import reverse
from payments.gateways.base import PaymentGateway
from payments.models import Payment
from django.shortcuts import redirect
from orders.models import Order

class PaymobGateway(PaymentGateway):
    def get_payment_url(self, payment: Payment) -> str:
        # Step 1: Get an authentication token from Paymob
        auth_payload = {
            "api_key": settings.PAYMOB_API_KEY,
            "username": settings.PAYMOB_USERNAME,
            "password": settings.PAYMOB_PASSWORD
        }

        headers = {
            "Content-Type": "application/json"  # Correct content type for Paymob API
        }

        auth_response = requests.post(
            'https://accept.paymobsolutions.com/api/auth/tokens',
            json=auth_payload,
            headers=headers,
            timeout=10
        )

        if auth_response.status_code != 201:
            print(f"Authentication failed with status {auth_response.status_code}: {auth_response.text}")
            raise Exception(f"Failed to authenticate with Paymob")

        auth_token = auth_response.json().get('token')
        if not auth_token:
            raise Exception("Authentication token is missing from the response")

        # Step 2: Create an order in Paymob, including billing data
        order_payload = {
            "amount_cents": int(payment.amount * 100),  # Amount in cents
            "currency": payment.currency.upper(),
            "merchant_order_ext_ref": f"order_{payment.order.id}",
            "delivery_needed": "false",  # Set delivery needed to "false"
            "redirect_url": reverse('payments:paymob_response'),  # This URL will handle the response
        }

        order_headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        order_response = requests.post(
            'https://accept.paymobsolutions.com/api/ecommerce/orders', 
            json=order_payload,  # Send order payload as JSON
            headers=order_headers
        )

        if order_response.status_code != 201:
            print(f"Order creation failed: {order_response.status_code}: {order_response.text}")
            raise Exception(f"Failed to create Paymob order")

        order_data = order_response.json()
        order_id = order_data['id']

        # Step 3: Create a payment token for Paymob's iframe
        payment_token_payload = {
            "amount_cents": int(payment.amount * 100),
            "currency": payment.currency.upper(),
            "order_id": order_id,
            "integration_id": settings.PAYMOB_INTEGRATION_ID,
            "billing_data": {
                "apartment": "NA",  # Default to "NA"
                "email": payment.order.user.email if payment.order.user.email else "NA",  # Ensure email is provided or set to "NA"
                "first_name": payment.order.user.first_name if payment.order.user.first_name else "NA",  # Ensure first name is provided or set to "NA"
                "last_name": payment.order.user.last_name if payment.order.user.last_name else "NA",  # Ensure last name is provided or set to "NA"
                "phone_number": payment.order.user.phone_number if payment.order.user.phone_number else "NA",  # Default to "NA"
                "country": "NA",  # Default to "NA"
                "state": "NA",  # Default to "NA"
                "city": "NA",  # Default to "NA"
                "street": "NA",  # Default to "NA"
                "building": "NA",  # Default to "NA"
                "floor": "NA",  # Default to None
                "zip": "NA",  # Default to "NA"
            },
        }

        payment_token_response = requests.post(
            'https://accept.paymobsolutions.com/api/acceptance/payment_keys', 
            json=payment_token_payload, 
            headers=order_headers
        )

        if payment_token_response.status_code != 201:
            print(f"Payment token creation failed: {payment_token_response.status_code}: {payment_token_response.text}")
            raise Exception(f"Failed to create Paymob payment token")

        payment_token_data = payment_token_response.json()
        payment_token = payment_token_data['token']

        # Step 4: Generate the iframe URL using the payment token
        iframe_url = f"https://accept.paymobsolutions.com/api/acceptance/iframes/884979?payment_token={payment_token}"

        # Step 5: Save Paymob session ID to the Payment model
        payment.payment_id = order_id
        payment.save()

        return iframe_url

    def process_response(self, request) -> None:
        # Handle the response from Paymob (for payment success, failure, etc.)
        payment_id = request.GET.get('payment_id')
        status = request.GET.get('status')
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            order = Order.objects.get(order_id=payment.order)
            # Check if the payment is successful or failed
            if status == 'SUCCESS':
                order.status = payment.status = 'Completed'
                payment.save()
                order.save()
                # Redirect to success page
                return redirect(reverse('payments:payments_success'))
            else:
                order.status = payment.status = 'Canceled'
                payment.save()
                order.save()
                # Redirect to failed payment page
                return redirect(reverse('payments:payment_cancel'))
        except Payment.DoesNotExist:
            raise Exception(f"Payment doesn't exist.")