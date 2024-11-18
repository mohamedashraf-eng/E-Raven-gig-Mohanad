import uuid
from django.db import models
from products.models import Product
from django.conf import settings
from django.utils.timezone import now

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    ]

    code = models.CharField(max_length=50, unique=True)  # Unique coupon code
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='fixed'
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # Discount value
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)  # Optional usage limit
    used_count = models.PositiveIntegerField(default=0)  # Tracks how many times the coupon has been used
    user = models.ManyToManyField(
        settings.AUTH_USER_MODEL,  # Reference the custom user model
        blank=True,
        help_text="Users who can use this coupon. Leave blank for all users."
    )

    def is_valid(self):
        """Check if the coupon is valid based on date, usage, and active status."""
        now_time = now()
        if not self.active or self.valid_from > now_time or self.valid_to < now_time:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def apply_discount(self, total_cost):
        """Calculate the new total after applying the discount."""
        if self.discount_type == 'fixed':
            return max(total_cost - self.discount_value, 0)  # Ensure total doesn't go below 0
        elif self.discount_type == 'percentage':
            return max(total_cost - (total_cost * (self.discount_value / 100)), 0)
        return total_cost

    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID primary key
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    coupon = models.ForeignKey(
        'Coupon',
        related_name='orders',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Coupon applied to this order, if any."
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Discount amount applied through the coupon."
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

    def get_total_cost(self):
        """Calculate the total cost including any discount applied."""
        subtotal = sum(item.get_cost() for item in self.items.all())
        if self.coupon and self.coupon.is_valid():
            self.discount_amount = self.coupon.apply_discount(subtotal) - subtotal
            return subtotal + self.discount_amount
        return subtotal

    def get_discount_display(self):
        """Return a user-friendly representation of the discount."""
        if self.coupon:
            if self.coupon.discount_type == 'fixed':
                return f'${self.coupon.discount_value:.2f} off'
            elif self.coupon.discount_type == 'percentage':
                return f'{self.coupon.discount_value:.0f}% off'
        return 'No discount'

    def get_order_items_summary(self):
        """Generate a summary of all items in the order."""
        return [{'product': item.product.name, 'quantity': item.quantity, 'price': item.price} for item in self.items.all()]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    
    class Meta:
        unique_together = [['order', 'product']]

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

    def get_cost(self):
        return self.price * self.quantity
