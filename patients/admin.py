from django.contrib import admin
from .models import Patient, Service

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'national_id', 'age', 'gender', 'phone', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'national_id')
    date_hierarchy = 'created_at'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('patient', 'service_type', 'date')
    list_filter = ('service_type', 'date')
    search_fields = ('patient__name',)