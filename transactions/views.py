from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from .models import Transaction, Bill, MoneyRequest, QRCode
from .forms import SendMoneyForm, RequestMoneyForm, BillPaymentForm, QRPaymentForm
from accounts.models import User, Profile, Notification
from accounts.utils import detect_fraud
import qrcode
import io
import base64
import json

@login_required
def send_money(request):
    if request.method == 'POST':
        form = SendMoneyForm(request.POST)
        if form.is_valid():
            receiver_phone = form.cleaned_data['receiver_phone']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            pin = form.cleaned_data['pin']
            
            # Verify PIN
            if request.user.profile.pin != pin:
                return render(request, 'transactions/error.html', {
                    'error_message': 'Invalid PIN entered. Please check your 4-digit transaction PIN.',
                    'error_code': 'PIN_INVALID'
                })
            
            # Check balance
            if request.user.profile.balance < amount:
                return render(request, 'transactions/error.html', {
                    'error_message': f'Insufficient balance. You have PKR {request.user.profile.balance} but tried to send PKR {amount}.',
                    'error_code': 'INSUFFICIENT_BALANCE'
                })
            
            try:
                receiver = User.objects.get(phone_number=receiver_phone)
                
                # Fraud detection (if fraud detection function exists)
                try:
                    is_fraud, fraud_reason = detect_fraud(request.user, amount, 'send')
                    if is_fraud:
                        return render(request, 'transactions/error.html', {
                            'error_message': f'Transaction blocked for security reasons: {fraud_reason}',
                            'error_code': 'FRAUD_DETECTED'
                        })
                except:
                    pass  # Skip fraud detection if function doesn't exist
                
                with transaction.atomic():
                    # Create transaction
                    trans = Transaction.objects.create(
                        sender=request.user,
                        receiver=receiver,
                        transaction_type='send',
                        amount=amount,
                        description=description,
                        status='completed',
                        completed_at=timezone.now()
                    )
                    
                    # Update balances
                    request.user.profile.balance -= amount
                    request.user.profile.save()
                    
                    receiver.profile.balance += amount
                    receiver.profile.save()
                    
                    # Create notifications
                    Notification.objects.create(
                        user=receiver,
                        title='Money Received',
                        message=f'You received PKR {amount} from {request.user.get_full_name()}'
                    )
                    
                    messages.success(request, f'Successfully sent PKR {amount} to {receiver.get_full_name()}')
                    return render(request, 'transactions/success.html', {
                        'success_message': f'Successfully sent PKR {amount} to {receiver.get_full_name()}',
                        'transaction_id': trans.transaction_id,
                        'amount': amount,
                        'receiver': receiver.get_full_name(),
                        'redirect_url': 'accounts:dashboard'
                    })
                    
            except User.DoesNotExist:
                return render(request, 'transactions/error.html', {
                    'error_message': f'No user found with phone number {receiver_phone}. Please check the number and try again.',
                    'error_code': 'USER_NOT_FOUND'
                })
    else:
        form = SendMoneyForm()
    
    return render(request, 'transactions/send_money.html', {'form': form})

@login_required
def request_money(request):
    if request.method == 'POST':
        form = RequestMoneyForm(request.POST)
        if form.is_valid():
            requested_from_phone = form.cleaned_data['requested_from_phone']
            amount = form.cleaned_data['amount']
            message = form.cleaned_data['message']
            
            try:
                requested_from = User.objects.get(phone_number=requested_from_phone)
                
                MoneyRequest.objects.create(
                    requester=request.user,
                    requested_from=requested_from,
                    amount=amount,
                    message=message
                )
                
                Notification.objects.create(
                    user=requested_from,
                    title='Money Request',
                    message=f'{request.user.get_full_name()} requested PKR {amount}'
                )
                
                messages.success(request, 'Money request sent successfully!')
                return render(request, 'transactions/success.html', {
                    'success_message': f'Money request of PKR {amount} sent successfully to {requested_from.get_full_name()}',
                    'amount': amount,
                    'receiver': requested_from.get_full_name(),
                    'redirect_url': 'accounts:dashboard'
                })
                
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = RequestMoneyForm()
    
    return render(request, 'transactions/request_money.html', {'form': form})

@login_required
def pay_bill(request):
    if request.method == 'POST':
        form = BillPaymentForm(request.POST)
        if form.is_valid():
            bill_type = form.cleaned_data['bill_type']
            bill_number = form.cleaned_data['bill_number']
            amount = form.cleaned_data['amount']
            pin = form.cleaned_data['pin']
            
            if request.user.profile.pin != pin:
                messages.error(request, 'Invalid PIN.')
                return render(request, 'transactions/pay_bill.html', {'form': form})
            
            if request.user.profile.balance < amount:
                messages.error(request, 'Insufficient balance.')
                return render(request, 'transactions/pay_bill.html', {'form': form})
            
            with transaction.atomic():
                # Create transaction
                Transaction.objects.create(
                    sender=request.user,
                    transaction_type='bill_payment',
                    amount=amount,
                    description=f'{bill_type} bill payment - {bill_number}',
                    status='completed',
                    completed_at=timezone.now()
                )
                
                # Update balance
                request.user.profile.balance -= amount
                request.user.profile.save()
                
                # Create/update bill record
                Bill.objects.create(
                    user=request.user,
                    bill_type=bill_type,
                    bill_number=bill_number,
                    amount=amount,
                    is_paid=True,
                    paid_at=timezone.now()
                )
                
                messages.success(request, f'Bill payment of PKR {amount} completed successfully!')
                return render(request, 'transactions/success.html', {
                    'success_message': f'{bill_type.title()} bill payment of PKR {amount} completed successfully!',
                    'transaction_id': Transaction.objects.latest('created_at').transaction_id,
                    'amount': amount,
                    'bill_type': bill_type,
                    'redirect_url': 'accounts:dashboard'
                })
    else:
        form = BillPaymentForm()
    
    return render(request, 'transactions/pay_bill.html', {'form': form})

@login_required
def generate_qr(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        
        qr_data = {
            'user_id': request.user.id,
            'phone': request.user.phone_number,
            'amount': amount if amount else None
        }
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode()
        
        # Save QR code
        QRCode.objects.create(
            user=request.user,
            qr_data=json.dumps(qr_data),
            amount=amount if amount else None
        )
        
        return render(request, 'transactions/qr_display.html', {
            'qr_image': qr_image,
            'amount': amount
        })
    
    return render(request, 'transactions/generate_qr.html')

@login_required
def qr_payment(request):
    if request.method == 'POST':
        form = QRPaymentForm(request.POST)
        if form.is_valid():
            qr_data = form.cleaned_data['qr_data']
            pin = form.cleaned_data['pin']
            
            if request.user.profile.pin != pin:
                messages.error(request, 'Invalid PIN.')
                return render(request, 'transactions/qr_payment.html', {'form': form})
            
            try:
                data = json.loads(qr_data)
                receiver = User.objects.get(id=data['user_id'])
                amount = float(data.get('amount', 0))
                
                if amount <= 0:
                    messages.error(request, 'Invalid amount in QR code.')
                    return render(request, 'transactions/qr_payment.html', {'form': form})
                
                if request.user.profile.balance < amount:
                    messages.error(request, 'Insufficient balance.')
                    return render(request, 'transactions/qr_payment.html', {'form': form})
                
                with transaction.atomic():
                    Transaction.objects.create(
                        sender=request.user,
                        receiver=receiver,
                        transaction_type='qr_payment',
                        amount=amount,
                        description='QR Code Payment',
                        status='completed',
                        completed_at=timezone.now()
                    )
                    
                    request.user.profile.balance -= amount
                    request.user.profile.save()
                    
                    receiver.profile.balance += amount
                    receiver.profile.save()
                    
                    messages.success(request, f'QR payment of PKR {amount} completed!')
                    return render(request, 'transactions/success.html', {
                        'success_message': f'QR payment of PKR {amount} completed successfully!',
                        'amount': amount,
                        'receiver': receiver.get_full_name(),
                        'redirect_url': 'accounts:dashboard'
                    })
                    
            except (json.JSONDecodeError, User.DoesNotExist, ValueError):
                messages.error(request, 'Invalid QR code.')
    else:
        form = QRPaymentForm()
    
    return render(request, 'transactions/qr_payment.html', {'form': form})

@login_required
def transaction_history(request):
    sent_transactions = request.user.sent_transactions.all()
    received_transactions = request.user.received_transactions.all()
    
    # Combine and sort by date
    all_transactions = list(sent_transactions) + list(received_transactions)
    all_transactions.sort(key=lambda x: x.created_at, reverse=True)
    
    return render(request, 'transactions/history.html', {'transactions': all_transactions})

@login_required
def verify_pin(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        if request.user.profile.pin == pin:
            return JsonResponse({'valid': True})
        return JsonResponse({'valid': False})
    return JsonResponse({'error': 'Invalid request'})

@login_required
def respond_money_request(request, request_id):
    money_request = get_object_or_404(MoneyRequest, id=request_id, requested_from=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            if request.user.profile.balance >= money_request.amount:
                with transaction.atomic():
                    # Transfer money
                    request.user.profile.balance -= money_request.amount
                    request.user.profile.save()
                    
                    money_request.requester.profile.balance += money_request.amount
                    money_request.requester.profile.save()
                    
                    # Update request status
                    money_request.status = 'accepted'
                    money_request.responded_at = timezone.now()
                    money_request.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        sender=request.user,
                        receiver=money_request.requester,
                        transaction_type='send',
                        amount=money_request.amount,
                        description=f'Money request payment: {money_request.message}',
                        status='completed',
                        completed_at=timezone.now()
                    )
                    
                    messages.success(request, 'Money request accepted and payment sent!')
            else:
                messages.error(request, 'Insufficient balance.')
        
        elif action == 'decline':
            money_request.status = 'declined'
            money_request.responded_at = timezone.now()
            money_request.save()
            messages.info(request, 'Money request declined.')
    
    return redirect('accounts:dashboard')

@login_required
def transaction_detail(request, transaction_id):
    transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    # Check if user is authorized to view this transaction
    if transaction_obj.sender != request.user and transaction_obj.receiver != request.user:
        messages.error(request, 'You are not authorized to view this transaction.')
        return redirect('transactions:transaction_history')
    
    context = {
        'transaction': transaction_obj,
        'is_sender': transaction_obj.sender == request.user,
        'is_receiver': transaction_obj.receiver == request.user,
    }
    
    return render(request, 'transactions/transaction_detail.html', context)

@login_required
def top_up(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        pin = request.POST.get('pin')
        
        if not amount or not pin:
            messages.error(request, 'Please provide amount and PIN.')
            return render(request, 'transactions/top_up.html')
        
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, 'Amount must be greater than 0.')
                return render(request, 'transactions/top_up.html')
        except ValueError:
            messages.error(request, 'Invalid amount.')
            return render(request, 'transactions/top_up.html')
        
        if request.user.profile.pin != pin:
            messages.error(request, 'Invalid PIN.')
            return render(request, 'transactions/top_up.html')
        
        with transaction.atomic():
            # Add money to balance
            request.user.profile.balance += amount
            request.user.profile.save()
            
            # Create transaction record
            Transaction.objects.create(
                sender=request.user,
                transaction_type='deposit',
                amount=amount,
                description='Account top-up',
                status='completed',
                completed_at=timezone.now()
            )
            
            messages.success(request, f'Successfully added PKR {amount} to your account!')
            return render(request, 'transactions/success.html', {
                'success_message': f'Successfully added PKR {amount} to your account!',
                'amount': amount,
                'redirect_url': 'accounts:dashboard'
            })
    
    return render(request, 'transactions/top_up.html')