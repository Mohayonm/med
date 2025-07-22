from django.urls import path
from medical import views

app_name = "medical"

urlpatterns = [
    path("equipment/", views.equipment_list, name="equipment_list"),
    path("equipment/new/", views.equipment_form, name="equipment_form"),
    path(
        "equipment/<int:equipment_id>/", views.equipment_detail, name="equipment_detail"
    ),
    path(
        "equipment/edit/<int:equipment_id>/",
        views.equipment_edit,
        name="equipment_edit",
    ),
    path(
        "equipment/delete/<int:equipment_id>/",
        views.equipment_delete,
        name="equipment_delete",
    ),
    path("edit/<int:service_id>/", views.service_edit, name="service_edit"),
    path("delete/<int:service_id>/", views.service_delete, name="service_delete"),
    path("detail/<int:service_id>/", views.service_detail, name="service_detail"),
    path(
        "financial/<int:service_id>/",
        views.service_financial_form,
        name="service_financial_form",
    ),
    path(
        "financial/edit/<int:service_id>/",
        views.service_financial_edit,
        name="service_financial_edit",
    ),
    path("<str:department>/new/", views.service_form, name="service_form"),
    path("<str:department>/", views.service_list, name="service_list"),
    path(
        "rehabilitation/new/",
        views.service_form,
        {"department": "rehabilitation"},
        name="rehabilitation_form",
    ),
    path(
        "rehabilitation/",
        views.service_list,
        {"department": "rehabilitation"},
        name="rehabilitation_list",
    ),
]
