from django.db import models
from accounts.models import User
import uuid

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('send', 'Send Money'),
        ('receive', 'Receive Money'),
        ('bill_payment', 'Bill Payment'),
        ('qr_payment', 'QR Payment'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.CharField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())[:12]
        super().save(*args, **kwargs)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions', null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']

class Bill(models.Model):
    BILL_TYPES = [
        ('electricity', 'Electricity'),
        ('gas', 'Gas'),
        ('water', 'Water'),
        ('internet', 'Internet'),
        ('mobile', 'Mobile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bill_type = models.CharField(max_length=20, choices=BILL_TYPES)
    bill_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MoneyRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money_requests_sent')
    requested_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='money_requests_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

class QRCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qr_data = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)