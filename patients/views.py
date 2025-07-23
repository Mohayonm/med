from django.shortcuts import render, redirect
from .models import Patient, Service
from .forms import PatientForm, ServiceForm

from django.shortcuts import render
from .models import Patient

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})

from django.shortcuts import render, redirect
from .models import Patient
from .forms import PatientForm

def add_patient(request):
    form = PatientForm()  # فرم به طور پیش‌فرض
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)  # برای دیباگ
            form.save()  # ذخیره مستقیم فرم
            return redirect('patients:patient_list')
    print(request.POST)  # برای دیباگ
    return render(request, 'patients/add_patient.html', {'form': form})



from django.shortcuts import render, get_object_or_404
from .models import Patient, Service
from .forms import ServiceForm

def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    services = Service.objects.filter(patient=patient)
    form = ServiceForm()
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.patient = patient
            service.save()
            return redirect('patients:patient_detail', pk=pk)
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'services': services,
        'form': form
    })