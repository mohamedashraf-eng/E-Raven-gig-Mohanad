from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

# cms/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.TextInput, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'phone_number', 'address', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
        }

class UserSecurityForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True, label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True, label="Confirm Password")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(UserSecurityForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(UserSecurityForm, self).clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Verify current password
        if not self.user.check_password(current_password):
            self.add_error('current_password', 'Current password is incorrect.')

        # Check if new passwords match
        if new_password and confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', 'New passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            self.user.set_password(new_password)
            if commit:
                self.user.save()
        return self.user
