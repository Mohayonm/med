from django import forms
from .models import Patient, Service

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "age", "phone", "national_id", "gender", "address", "birth_date"]
        labels = {
            "name": "نام بیمار",
            "age": "سن",
            "phone": "شماره تماس",
            "national_id": "کد ملی",
            "gender": "جنسیت",
            "address": "آدرس",
            "birth_date": "تاریخ تولد",
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["service_type", "description"]
        labels = {
            "service_type": "نوع خدمت",
            "description": "توضیحات",
        }