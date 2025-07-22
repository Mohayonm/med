from django.contrib import admin
from tickets.models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'sender', 'recipient', 'status', 'priority', 'department', 'created_at')
    list_filter = ('status', 'priority', 'department')
    search_fields = ('subject', 'content', 'sender__user_name', 'recipient__user_name')
    readonly_fields = ('created_at', 'update_at')
    list_per_page = 20
