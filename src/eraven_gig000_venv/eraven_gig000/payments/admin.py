from django.contrib import admin
from .models import Payment

# Customizing the display of Payment in the admin interface
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'gateway', 'amount', 'currency', 'status', 'timestamp')
    list_filter = ('gateway', 'status', 'currency')
    search_fields = ('order__id', 'payment_id', 'gateway')
    readonly_fields = ('id', 'payment_id', 'order', 'amount', 'currency', 'timestamp')  # Make some fields readonly
    
    # Optionally, you can add ordering
    ordering = ('-timestamp',)

# Register the Payment model with the custom admin class
admin.site.register(Payment, PaymentAdmin)
