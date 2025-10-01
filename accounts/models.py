from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid

class User(AbstractUser):
    phone_regex = RegexValidator(regex=r'^0\d{10}$', message='Enter a valid 11-digit phone number starting with 0')
    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=15, unique=True, help_text='13-digit CNIC (e.g., 12345-1234567-1)')
    date_of_birth = models.DateField()
    address = models.TextField()
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    account_number = models.CharField(max_length=20, unique=True)
    pin = models.CharField(max_length=4, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            # Generate unique 12-digit account number
            import random
            while True:
                account_num = f"CE{random.randint(1000000000, 9999999999)}"
                if not Profile.objects.filter(account_number=account_num).exists():
                    self.account_number = account_num
                    break
        super().save(*args, **kwargs)

class KYCDocument(models.Model):
    DOCUMENT_TYPES = [
        ('cnic_front', 'CNIC Front'),
        ('cnic_back', 'CNIC Back'),
        ('selfie', 'Selfie'),
        ('utility_bill', 'Utility Bill'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = models.ImageField(upload_to='kyc_documents/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewer_notes = models.TextField(blank=True)

class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20)  # registration, login, transaction
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)