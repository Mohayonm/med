from django.urls import path
from exports import views
from exports.utils import export_services_excel, export_equipment_excel, export_tickets_excel

app_name = "exports"

urlpatterns = [
    # Dashboard
    path("main/", views.export_dashboard, name="dashboard"),
    
    # Database download (only for staff/admin)
    path("database/download/", views.download_database, name="download_database"),
    
    # Service exports
    path("services/<str:department>/", export_services_excel, name="services_by_department"),
    path("services/all/", export_services_excel, {'department': None}, name="all_services"),
    
    # Equipment export
    path("equipment/", export_equipment_excel, name="equipment"),
    
    # Tickets export
    path("tickets/", export_tickets_excel, name="tickets"),
]
