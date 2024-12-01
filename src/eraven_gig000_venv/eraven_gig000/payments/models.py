import uuid
from django.db import models
from django.urls import reverse
from orders.models import Order

class Payment(models.Model):
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('paymob', 'Paymob'),
        # Add other gateways here
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID primary key
    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES)
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Unique UUID
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EGP')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')  # e.g., pending, completed, failed

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Payment {self.id} for Order {self.order.id} via {self.get_gateway_display()}'

    def get_payment_url(self):
        """Return the URL to redirect the user for payment."""
        # Lazy import to avoid circular import issues
        from .gateways.base import PaymentGateway
        gateway_class = PaymentGateway.get_gateway_class(self.gateway)
        return gateway_class().get_payment_url(self)
