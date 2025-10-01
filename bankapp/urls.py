from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render

def webapp_home(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'landing.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', webapp_home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('admin-panel/', include('admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)