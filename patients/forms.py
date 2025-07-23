from django import forms
from .models import Patient, Service
from django_jalali.forms import jDateField

class PatientForm(forms.ModelForm):
    birth_date = jDateField(
        widget=forms.TextInput(attrs={
            'class': 'jalali_datepicker',
            'placeholder': 'YYYY/MM/DD (مثال: 1404/05/01)',
        }),
        label='تاریخ تولد',
        input_formats=['%Y/%m/%d']  # فرمت دقیق برای تاریخ شمسی
    )

    class Meta:
        model = Patient
        fields = ['name', 'age', 'phone', 'national_id', 'gender', 'address', 'birth_date']
        widgets = {
            'gender': forms.Select(choices=[('', 'انتخاب جنسیت'), ('M', 'مرد'), ('F', 'زن')]),
            'address': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'نام بیمار',
            'age': 'سن',
            'phone': 'شماره تماس',
            'national_id': 'کد ملی',
            'gender': 'جنسیت',
            'address': 'آدرس',
            'birth_date': 'تاریخ تولد',
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            return birth_date
        return None

class ServiceForm(forms.ModelForm):
    date = jDateField(
        widget=forms.TextInput(attrs={
            'class': 'jalali_datepicker',
            'placeholder': 'YYYY/MM/DD (مثال: 1404/05/01)',
        }),
        label='تاریخ خدمت',
        input_formats=['%Y/%m/%d']  # فرمت دقیق برای تاریخ شمسی
    )

    class Meta:
        model = Service
        fields = ['service_type', 'description', 'date']
        widgets = {
            'service_type': forms.Select(choices=[
                ('rehabilitation', 'بازتوانی'),
                ('medical', 'پزشکی'),
                ('nursing', 'پرستاری'),
                ('care', 'مراقبت'),
            ]),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'service_type': 'نوع خدمت',
            'description': 'توضیحات',
            'date': 'تاریخ خدمت',
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            return date
        return None