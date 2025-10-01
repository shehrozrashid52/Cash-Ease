from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .models import User, Profile, KYCDocument, Notification
from .forms import RegistrationForm, LoginForm, ProfileForm, KYCUploadForm, PinChangeForm
import random
from datetime import timedelta
from decimal import Decimal

def register(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data directly
                username = request.POST.get('username')
                email = request.POST.get('email')
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                phone_number = request.POST.get('phone_number')
                cnic = request.POST.get('cnic')
                date_of_birth = request.POST.get('date_of_birth')
                address = request.POST.get('address')
                pin = request.POST.get('pin')
                confirm_pin = request.POST.get('confirm_pin')
                
                # Basic validation
                if password1 != password2:
                    messages.error(request, 'Passwords do not match')
                    return render(request, 'accounts/register.html')
                
                if pin != confirm_pin:
                    messages.error(request, 'PINs do not match')
                    return render(request, 'accounts/register.html')
                
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists')
                    return render(request, 'accounts/register.html')
                
                if User.objects.filter(phone_number=phone_number).exists():
                    messages.error(request, 'Phone number already registered')
                    return render(request, 'accounts/register.html')
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    is_active=True,
                    is_verified=True
                )
                
                # Create profile
                Profile.objects.create(
                    user=user,
                    full_name=f"{first_name} {last_name}".strip() or username,
                    cnic=cnic,
                    date_of_birth=date_of_birth,
                    address=address,
                    balance=Decimal('0.00'),
                    pin=pin
                )
                
                messages.success(request, 'Account created successfully! Please login to continue.')
                return redirect('accounts:login')
                
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user:
                if user.is_blocked:
                    messages.error(request, 'Your account has been blocked.')

                else:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    # Create profile if it doesn't exist
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        import random
        # Generate unique CNIC
        while True:
            cnic = f"42101-{random.randint(1000000, 9999999)}-{random.randint(1, 9)}"
            if not Profile.objects.filter(cnic=cnic).exists():
                break
        
        profile = Profile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            cnic=cnic,
            date_of_birth='1990-01-01',
            address='Default Address',
            balance=Decimal('0.00'),
            pin=None
        )
    
    # Get all transactions for the user
    from transactions.models import Transaction
    from django.db.models import Q, Sum
    from datetime import datetime, timedelta
    
    # Get recent transactions (both sent and received)
    recent_transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')[:5]
    
    # Calculate statistics for current month
    current_month = datetime.now().replace(day=1)
    
    # Total transactions this month
    total_transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        created_at__gte=current_month
    ).count()
    
    # Money sent this month
    money_sent = Transaction.objects.filter(
        sender=request.user,
        created_at__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Money received this month
    money_received = Transaction.objects.filter(
        receiver=request.user,
        created_at__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    try:
        pending_requests = request.user.money_requests_received.filter(status='pending')
    except:
        pending_requests = []
    
    try:
        notifications = request.user.notification_set.filter(is_read=False)[:5]
    except:
        notifications = []
    
    context = {
        'profile': profile,
        'recent_transactions': recent_transactions,
        'pending_requests': pending_requests,
        'notifications': notifications,
        'total_transactions': total_transactions,
        'money_sent': money_sent,
        'money_received': money_received,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    profile_obj = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile_obj)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def kyc_upload(request):
    if request.method == 'POST':
        form = KYCUploadForm(request.POST, request.FILES)
        if form.is_valid():
            kyc_doc = form.save(commit=False)
            kyc_doc.user = request.user
            kyc_doc.save()
            messages.success(request, 'KYC document uploaded successfully!')
            return redirect('accounts:kyc_upload')
    else:
        form = KYCUploadForm()
    
    user_docs = KYCDocument.objects.filter(user=request.user)
    return render(request, 'accounts/kyc_upload.html', {'form': form, 'documents': user_docs})

@login_required
def change_pin(request):
    profile = request.user.profile
    is_first_time = not profile.pin
    
    if request.method == 'POST':
        form = PinChangeForm(request.POST)
        if form.is_valid():
            current_pin = form.cleaned_data.get('current_pin')
            new_pin = form.cleaned_data['new_pin']
            
            # Validate current PIN if not first time
            if not is_first_time and profile.pin != current_pin:
                messages.error(request, 'Current PIN is incorrect.')
                return render(request, 'accounts/change_pin.html', {'form': form, 'is_first_time': is_first_time})
            
            profile.pin = new_pin
            profile.save()
            
            if is_first_time:
                messages.success(request, 'PIN created successfully! You can now make transactions.')
            else:
                messages.success(request, 'PIN changed successfully!')
            return redirect('accounts:dashboard')
    else:
        form = PinChangeForm()
    
    return render(request, 'accounts/change_pin.html', {'form': form, 'is_first_time': is_first_time})

@login_required
def notifications(request):
    notifications = request.user.notification_set.all().order_by('-created_at')
    # Mark as read
    notifications.update(is_read=True)
    return render(request, 'accounts/notifications.html', {'notifications': notifications})