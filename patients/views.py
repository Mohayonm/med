from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient, Service
from .forms import PatientForm, ServiceForm

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, "patients/patient_list.html", {"patients": patients})

def add_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("patients:patient_list")
    else:
        form = PatientForm()
    return render(request, "patients/add_patient.html", {"form": form})

def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    services = patient.services.all()
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.patient = patient
            service.save()
            return redirect("patients:patient_detail", patient_id=patient.id)
    else:
        form = ServiceForm()
    return render(request, "patients/patient_detail.html", {
        "patient": patient,
        "services": services,
        "form": form,
    })