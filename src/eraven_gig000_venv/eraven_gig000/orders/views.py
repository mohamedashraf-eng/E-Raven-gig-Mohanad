# orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import OrderItem, Order
from ums.decorators import custom_login_required
from django.urls import reverse
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Coupon, Order, OrderItem, Product
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from .models import Coupon, Order, OrderItem, Product
from ums.decorators import custom_login_required
import json
from django.utils import timezone

@custom_login_required
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cost = product.price * quantity
        total += cost
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'cost': cost
        })
    return render(request, 'orders/cart_detail.html', {'cart_items': cart_items, 'total': total})

@custom_login_required
def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)  # Ensure product_id is a string
    # Only add the bundle 1x
    cart[product_id_str] = 1
    request.session['cart'] = cart
    return redirect('orders:cart_detail')

@custom_login_required
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)  # Ensure product_id is a string
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('orders:cart_detail')

@custom_login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('products:product_list')

    # Initialize coupon-related session variables
    if 'coupon_id' not in request.session:
        request.session['coupon_id'] = None

    # Handle order placement
    if request.method == 'POST' and 'place_order' in request.POST:
        coupon_id = request.session.get('coupon_id')
        coupon = None
        discount_amount = 0

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                if not coupon.is_valid():
                    messages.error(request, "The applied coupon is no longer valid.")
                    coupon = None
            except Coupon.DoesNotExist:
                messages.error(request, "The applied coupon does not exist.")
                coupon = None

        # Calculate total cost with discount
        total_cost = 0
        order_items = []
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cost = product.price * quantity
                total_cost += cost
                order_items.append({
                    'product': product,
                    'quantity': quantity,
                    'cost': cost
                })
            except Product.DoesNotExist:
                messages.error(request, "A product in your cart does not exist.")
                return redirect('products:product_list')

        # Apply coupon discount
        if coupon and coupon.is_valid():
            if coupon.discount_type == 'fixed':
                discount_amount = min(coupon.discount_value, total_cost)
                total_cost -= discount_amount
            elif coupon.discount_type == 'percentage':
                discount_amount = min((coupon.discount_value / 100) * total_cost, total_cost)
                total_cost -= discount_amount

            # Increment used count
            coupon.used_count += 1
            coupon.save()

        # Create Order with status 'pending'
        order = Order.objects.create(
            user=request.user,
            total_cost=total_cost,
            status='pending',
            coupon=coupon,
            discount_amount=discount_amount
        )
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['product'].price,
                quantity=item['quantity'],
                cost=item['cost']  # Assign the calculated cost
            )

        # Clear the cart and coupon
        request.session['cart'] = {}
        request.session['coupon_id'] = None

        messages.success(request, "Your order has been placed successfully!")
        return redirect(reverse('payments:select_payment_method', args=[order.id]))

    # Calculate total cost
    total_cost = 0
    order_items = []
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            cost = product.price * quantity
            total_cost += cost
            order_items.append({
                'product': product,
                'quantity': quantity,
                'cost': cost
            })
        except Product.DoesNotExist:
            messages.error(request, "A product in your cart does not exist.")
            return redirect('products:product_list')

    # Apply coupon discount if any
    coupon = None
    discount_amount = 0
    if request.session.get('coupon_id'):
        try:
            coupon = Coupon.objects.get(id=request.session['coupon_id'])
            if coupon.is_valid():
                if coupon.discount_type == 'fixed':
                    discount_amount = coupon.discount_value
                elif coupon.discount_type == 'percentage':
                    discount_amount = (coupon.discount_value / 100) * total_cost
                total_cost = coupon.apply_discount(total_cost)
            else:
                messages.error(request, "The applied coupon is no longer valid.")
                request.session['coupon_id'] = None
                coupon = None
        except Coupon.DoesNotExist:
            messages.error(request, "The applied coupon does not exist.")
            request.session['coupon_id'] = None
            coupon = None

    context = {
        'order_items': order_items,
        'total_cost': total_cost,
        'coupon': coupon,
        'discount_amount': discount_amount if coupon else 0.00
    }
    return render(request, 'orders/checkout.html', context)

@custom_login_required
@require_POST
@require_POST
def apply_coupon(request):
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code', '').strip()

        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'No coupon code provided.'})

        # Fetch the coupon
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or inactive coupon.'})

        # Check if coupon is expired
        if coupon.valid_to < timezone.now() or coupon.valid_from > timezone.now():
            return JsonResponse({'success': False, 'message': 'This coupon is not currently valid.'})

        # Check usage limits
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return JsonResponse({'success': False, 'message': 'This coupon has reached its usage limit.'})

        # If the coupon is user-specific, verify the user
        if coupon.user.exists() and request.user not in coupon.user.all():
            return JsonResponse({'success': False, 'message': 'You are not eligible to use this coupon.'})

        # Check if a coupon is already applied
        if request.session.get('coupon_id'):
            existing_coupon = Coupon.objects.get(id=request.session['coupon_id'])
            return JsonResponse({'success': False, 'message': f"Coupon '{existing_coupon.code}' is already applied."})

        # Calculate discount based on cart total
        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({'success': False, 'message': 'Your cart is empty.'})

        # Calculate cart total
        total_cost = 0
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total_cost += product.price * quantity
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'A product in your cart does not exist.'})

        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount_amount = (coupon.discount_value / 100) * total_cost
        elif coupon.discount_type == 'fixed':
            discount_amount = coupon.discount_value
        else:
            return JsonResponse({'success': False, 'message': 'Invalid coupon type.'})

        # Ensure discount does not exceed total cost
        discount_amount = min(discount_amount, total_cost)

        # Store the coupon in session
        request.session['coupon_id'] = coupon.id

        return JsonResponse({
            'success': True,
            'message': f"Coupon '{coupon.code}' applied successfully!",
            'coupon_code': coupon.code,
            'discount_amount': f"${discount_amount:.2f}",
            'new_total': f"${total_cost - discount_amount:.2f}",
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred while applying the coupon.'})

@custom_login_required
@require_POST
def remove_coupon(request):
    try:
        coupon_id = request.session.get('coupon_id')
        if not coupon_id:
            return JsonResponse({'success': False, 'message': 'No coupon to remove.'})

        coupon = get_object_or_404(Coupon, id=coupon_id)

        # Remove the coupon from the session
        request.session['coupon_id'] = None

        # Calculate the new total cost without the coupon
        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({'success': False, 'message': 'Your cart is empty.'})

        # Calculate cart total
        total_cost = 0
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total_cost += product.price * quantity
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'A product in your cart does not exist.'})

        return JsonResponse({
            'success': True,
            'message': 'Coupon removed successfully.',
            'new_total': f"${total_cost:.2f}",
        })

    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid coupon.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred while removing the coupon.'})