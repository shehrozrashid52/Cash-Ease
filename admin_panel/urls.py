from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('transactions/', views.transaction_management, name='transaction_management'),
    path('kyc-review/', views.kyc_review, name='kyc_review'),
    path('approve-kyc/<int:doc_id>/', views.approve_kyc, name='approve_kyc'),
    path('reject-kyc/<int:doc_id>/', views.reject_kyc, name='reject_kyc'),
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock-user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('reports/', views.financial_reports, name='reports'),
]