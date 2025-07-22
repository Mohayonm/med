from django.contrib import admin
from medical.models import ServiceRequest, ServiceFinancialInfo, EquipmentRequest


class ServiceFinancialInfoInline(admin.StackedInline):
    model = ServiceFinancialInfo
    extra = 0


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'department', 'status', 'service_performed', 'created_at')
    list_filter = ('department', 'status', 'service_performed')
    search_fields = ('name', 'phone', 'address')
    readonly_fields = ('created_at', 'update_at')
    inlines = [ServiceFinancialInfoInline]
    list_per_page = 20


@admin.register(ServiceFinancialInfo)
class ServiceFinancialInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_request', 'specialist_name', 'total_amount', 'payment_receiver', 'created_at')
    list_filter = ('payment_receiver',)
    search_fields = ('specialist_name', 'description')
    readonly_fields = ('created_at', 'update_at')
    list_per_page = 20


@admin.register(EquipmentRequest)
class EquipmentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_type', 'quantity', 'total_amount', 'payment_receiver', 'created_at')
    list_filter = ('payment_receiver',)
    search_fields = ('item_type', 'description')
    readonly_fields = ('created_at', 'update_at')
    list_per_page = 20
