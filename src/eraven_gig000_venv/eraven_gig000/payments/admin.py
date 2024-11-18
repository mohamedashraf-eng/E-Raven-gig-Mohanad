from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'gateway', 'payment_id', 'amount', 'currency', 'status', 'timestamp']
    list_filter = ['gateway', 'status', 'timestamp']
    search_fields = ['order__id', 'payment_id']
