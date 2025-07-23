from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('tickets/', include('tickets.urls', namespace='tickets')),
    path('equipment/', include('medical.urls', namespace='medical')),
    path('exports/', include('exports.urls', namespace='exports')),  # اضافه کردن exports
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)