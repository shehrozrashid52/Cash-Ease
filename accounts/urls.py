from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('kyc-upload/', views.kyc_upload, name='kyc_upload'),
    path('change-pin/', views.change_pin, name='change_pin'),
    path('notifications/', views.notifications, name='notifications'),
]