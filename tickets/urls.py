from django.urls import path

from tickets import views

app_name = "tickets"

urlpatterns = [
    path("tickets/new/", views.create_ticket, name="create_ticket"),
    path("tickets/inbox/", views.ticket_inbox, name="ticket_inbox"),
    path("tickets/sent/", views.ticket_sent, name="ticket_sent"),
    path("tickets/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    path(
        "tickets/<int:ticket_id>/status/",
        views.update_ticket_status,
        name="update_ticket_status",
    ),
    path("tickets/all-tickets/", views.admin_all_tickets, name="admin_all_tickets"),
]
