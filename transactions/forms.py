from django import forms
from .models import Transaction, Bill

class SendMoneyForm(forms.Form):
    receiver_phone = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Receiver Phone Number'})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (PKR)'})
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description (optional)'})
    )
    pin = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter PIN'})
    )

class RequestMoneyForm(forms.Form):
    requested_from_phone = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (PKR)'})
    )
    message = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Message (optional)'})
    )

class BillPaymentForm(forms.Form):
    BILL_TYPES = [
        ('electricity', 'Electricity'),
        ('gas', 'Gas'),
        ('water', 'Water'),
        ('internet', 'Internet'),
        ('mobile', 'Mobile'),
    ]
    
    bill_type = forms.ChoiceField(
        choices=BILL_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    bill_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bill Number'})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (PKR)'})
    )
    pin = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter PIN'})
    )

class QRPaymentForm(forms.Form):
    qr_data = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Scan QR or paste data', 'rows': 3})
    )
    pin = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter PIN'})
    )