from django.shortcuts import render, redirect
from .models import Patient, Service
from .forms import PatientForm, ServiceForm

from django.shortcuts import render
from .models import Patient

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})

def add_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patients:patient_list')
    else:
        form = PatientForm()
    return render(request, 'patients/add_patient.html', {'form': form})

def patient_detail(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    services = Service.objects.filter(patient=patient)
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.patient = patient
            service.save()
            return redirect('patients:patient_detail', patient_id=patient_id)
    else:
        form = ServiceForm()
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'services': services,
        'form': form
    })