from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('add/', views.add_patient, name='add_patient'),
    path("<int:patient_id>/", views.patient_detail, name="patient_detail"),
]