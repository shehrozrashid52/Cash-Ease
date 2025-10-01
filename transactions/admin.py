from django.contrib import admin
from .models import Transaction, Bill, MoneyRequest, QRCode

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'sender', 'receiver', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('transaction_id', 'sender__username', 'receiver__username')
    readonly_fields = ('transaction_id', 'created_at')

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('user', 'bill_type', 'bill_number', 'amount', 'is_paid', 'due_date')
    list_filter = ('bill_type', 'is_paid', 'due_date')
    search_fields = ('user__username', 'bill_number')

@admin.register(MoneyRequest)
class MoneyRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'requested_from', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__username', 'requested_from__username')

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username',)