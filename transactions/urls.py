from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('send-money/', views.send_money, name='send_money'),
    path('request-money/', views.request_money, name='request_money'),
    path('pay-bill/', views.pay_bill, name='pay_bill'),
    path('qr-payment/', views.qr_payment, name='qr_payment'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('verify-pin/', views.verify_pin, name='verify_pin'),
    path('respond-request/<int:request_id>/', views.respond_money_request, name='respond_request'),
    path('top-up/', views.top_up, name='top_up'),
    path('transaction-detail/<str:transaction_id>/', views.transaction_detail, name='transaction_detail'),
]