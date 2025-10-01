from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, KYCDocument, OTPVerification, Notification

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_verified', 'is_blocked', 'date_joined')
    list_filter = ('is_verified', 'is_blocked', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'is_verified', 'is_blocked')}),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'account_number', 'balance', 'created_at')
    search_fields = ('user__username', 'full_name', 'account_number', 'cnic')
    list_filter = ('created_at',)

@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'uploaded_at', 'reviewed_at')
    list_filter = ('document_type', 'status', 'uploaded_at')
    search_fields = ('user__username',)

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'purpose', 'is_used', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_used', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title')

admin.site.register(User, CustomUserAdmin)