from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, Profile, KYCDocument, Notification
from transactions.models import Transaction, Bill

@staff_member_required
def admin_dashboard(request):
    # Statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True, is_blocked=False).count()
    total_transactions = Transaction.objects.count()
    total_volume = Transaction.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_kyc = KYCDocument.objects.filter(status='pending').count()
    
    # Recent transactions
    recent_transactions = Transaction.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_transactions': total_transactions,
        'total_volume': total_volume,
        'pending_kyc': pending_kyc,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@staff_member_required
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        users = users.filter(
            username__icontains=search
        ) | users.filter(
            phone_number__icontains=search
        ) | users.filter(
            email__icontains=search
        )
    
    return render(request, 'admin_panel/user_management.html', {'users': users})

@staff_member_required
def transaction_management(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        transactions = transactions.filter(created_at__gte=date_from)
    if date_to:
        transactions = transactions.filter(created_at__lte=date_to)
    
    return render(request, 'admin_panel/transaction_management.html', {'transactions': transactions})

@staff_member_required
def kyc_review(request):
    pending_docs = KYCDocument.objects.filter(status='pending').order_by('-uploaded_at')
    return render(request, 'admin_panel/kyc_review.html', {'documents': pending_docs})

@staff_member_required
def approve_kyc(request, doc_id):
    doc = get_object_or_404(KYCDocument, id=doc_id)
    doc.status = 'approved'
    doc.reviewed_at = timezone.now()
    doc.save()
    
    # Notify user
    Notification.objects.create(
        user=doc.user,
        title='KYC Approved',
        message=f'Your {doc.get_document_type_display()} has been approved.'
    )
    
    messages.success(request, f'KYC document approved for {doc.user.username}')
    return redirect('admin_panel:kyc_review')

@staff_member_required
def reject_kyc(request, doc_id):
    doc = get_object_or_404(KYCDocument, id=doc_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        doc.status = 'rejected'
        doc.reviewed_at = timezone.now()
        doc.reviewer_notes = notes
        doc.save()
        
        # Notify user
        Notification.objects.create(
            user=doc.user,
            title='KYC Rejected',
            message=f'Your {doc.get_document_type_display()} was rejected. Reason: {notes}'
        )
        
        messages.success(request, f'KYC document rejected for {doc.user.username}')
        return redirect('admin_panel:kyc_review')
    
    return render(request, 'admin_panel/reject_kyc.html', {'document': doc})

@staff_member_required
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = True
    user.save()
    
    # Notify user
    Notification.objects.create(
        user=user,
        title='Account Blocked',
        message='Your account has been temporarily blocked. Contact support for assistance.'
    )
    
    messages.success(request, f'User {user.username} has been blocked.')
    return redirect('admin_panel:user_management')

@staff_member_required
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = False
    user.save()
    
    # Notify user
    Notification.objects.create(
        user=user,
        title='Account Unblocked',
        message='Your account has been unblocked. You can now use all services.'
    )
    
    messages.success(request, f'User {user.username} has been unblocked.')
    return redirect('admin_panel:user_management')

@staff_member_required
def financial_reports(request):
    # Daily transactions for last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_transactions = Transaction.objects.filter(
        created_at__gte=thirty_days_ago,
        status='completed'
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        count=Count('id'),
        volume=Sum('amount')
    ).order_by('day')
    
    # Transaction type breakdown
    transaction_types = Transaction.objects.filter(
        status='completed'
    ).values('transaction_type').annotate(
        count=Count('id'),
        volume=Sum('amount')
    )
    
    # Top users by transaction volume
    top_users = User.objects.annotate(
        transaction_volume=Sum('sent_transactions__amount')
    ).filter(
        transaction_volume__isnull=False
    ).order_by('-transaction_volume')[:10]
    
    context = {
        'daily_transactions': daily_transactions,
        'transaction_types': transaction_types,
        'top_users': top_users,
    }
    return render(request, 'admin_panel/reports.html', context)