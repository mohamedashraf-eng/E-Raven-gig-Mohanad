from django.contrib import admin
from .models import Order, OrderItem, Coupon

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created', 'updated', 'get_total_cost']
    list_filter = ['created', 'updated']
    search_fields = ['user__username', 'id']

    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Total Cost'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity', 'get_cost']
    list_filter = ['order', 'product']
    search_fields = ['order__id', 'product__name']

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Cost'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'active', 'used_count', 'max_uses')
    list_filter = ('active', 'discount_type', 'valid_from', 'valid_to')
    search_fields = ('code',)