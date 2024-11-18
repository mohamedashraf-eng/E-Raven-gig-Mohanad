# orders/forms.py

from django import forms

class CheckoutForm(forms.Form):
    # Personal Information
    full_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    
    # Shipping Address
    address_line1 = forms.CharField(max_length=255, required=True)
    address_line2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    postal_code = forms.CharField(max_length=20, required=True)
    country = forms.ChoiceField(choices=[('US', 'United States'), ('CA', 'Canada'), ...], required=True)
    
    # Payment Information
    card_number = forms.CharField(max_length=16, required=True)
    expiry_date = forms.CharField(max_length=5, required=True)
    cvv = forms.CharField(max_length=4, required=True)
