import random
import string

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp(phone_number, otp_code):
    """Simulate sending OTP via SMS"""
    print(f"Sending OTP {otp_code} to {phone_number}")
    # In production, integrate with SMS service like Twilio
    return True

def detect_fraud(user, amount, transaction_type):
    """Basic fraud detection logic"""
    from transactions.models import Transaction
    from datetime import timedelta
    from django.utils import timezone
    
    # Check for multiple large transactions in short time
    recent_transactions = Transaction.objects.filter(
        sender=user,
        created_at__gte=timezone.now() - timedelta(hours=1),
        status='completed'
    )
    
    total_recent = sum(t.amount for t in recent_transactions)
    
    # Flag if more than 50000 in last hour
    if total_recent + amount > 50000:
        return True, "Multiple large transactions detected"
    
    # Flag if single transaction > 100000
    if amount > 100000:
        return True, "Large transaction amount"
    
    return False, "Transaction appears normal"