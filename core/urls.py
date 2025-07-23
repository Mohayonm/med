from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('patients/', include('patients.urls')),  # برای اپلیکیشن patients
    path('', include('homepage.urls')),  # برای داشبورد
    path('accounts/', include('django.contrib.auth.urls')),  # برای لاگین، لاگ‌اوت و غیره
    path('tickets/', include('tickets.urls')),  # برای اپلیکیشن tickets
    path('equipment/', include('medical.urls')),  # برای اپلیکیشن medical
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)