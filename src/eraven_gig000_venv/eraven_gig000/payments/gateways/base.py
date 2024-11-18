# payments/gateways/base.py

from abc import ABC, abstractmethod
from payments.models import Payment

class PaymentGateway(ABC):
    @abstractmethod
    def get_payment_url(self, payment: Payment) -> str:
        """Return the URL to which the user should be redirected to complete the payment."""
        pass

    @abstractmethod
    def process_response(self, request) -> None:
        """Process the payment gateway's response after the user completes the payment."""
        pass

    @classmethod
    def get_gateway_class(cls, gateway_name):
        """Retrieve the gateway class based on the gateway name."""
        gateway_classes = {
            'stripe': 'payments.gateways.stripe.StripeGateway',
            'paypal': 'payments.gateways.paypal.PayPalGateway',
            # Add other gateways here
        }
        path = gateway_classes.get(gateway_name)
        if path:
            module_path, class_name = path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        raise ValueError(f"No gateway found for name: {gateway_name}")
