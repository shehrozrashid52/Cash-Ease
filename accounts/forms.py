from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, KYCDocument

class RegistrationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=11, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03101234567', 'pattern': '^0\d{10}$'}),
        help_text='Enter 11-digit number starting with 0'
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cnic = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345-1234567-1'}),
        help_text='Enter 13-digit CNIC with dashes'
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    pin = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter 4-digit PIN'}),
        help_text='Create a secure 4-digit PIN for transactions'
    )
    confirm_pin = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm PIN'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        pin = cleaned_data.get('pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        # Phone number validation
        if phone_number:
            if len(phone_number) != 11:
                raise forms.ValidationError('Phone number must be exactly 11 digits')
            if not phone_number.startswith('0'):
                raise forms.ValidationError('Phone number must start with 0')
            if not phone_number.isdigit():
                raise forms.ValidationError('Phone number must contain only digits')
        
        # PIN validation
        if pin and confirm_pin:
            if pin != confirm_pin:
                raise forms.ValidationError('PINs do not match')
            if not pin.isdigit():
                raise forms.ValidationError('PIN must contain only numbers')
            if len(set(pin)) == 1:
                raise forms.ValidationError('PIN cannot be all same digits (e.g., 1111)')
            if pin in ['1234', '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999']:
                raise forms.ValidationError('PIN is too common. Please choose a more secure PIN')
        
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'cnic', 'date_of_birth', 'address', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class KYCUploadForm(forms.ModelForm):
    class Meta:
        model = KYCDocument
        fields = ['document_type', 'document_file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PinChangeForm(forms.Form):
    current_pin = forms.CharField(
        max_length=4, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current PIN'}),
        required=False
    )
    new_pin = forms.CharField(
        max_length=4, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New 4-digit PIN'})
    )
    confirm_pin = forms.CharField(
        max_length=4, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new PIN'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get('new_pin')
        confirm_pin = cleaned_data.get('confirm_pin')

        if new_pin and confirm_pin:
            if new_pin != confirm_pin:
                raise forms.ValidationError("New PIN and confirmation don't match.")
            if not new_pin.isdigit():
                raise forms.ValidationError('PIN must contain only numbers')
            if len(set(new_pin)) == 1:
                raise forms.ValidationError('PIN cannot be all same digits (e.g., 1111)')
            if new_pin in ['1234', '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999']:
                raise forms.ValidationError('PIN is too common. Please choose a more secure PIN')
        
        return cleaned_data