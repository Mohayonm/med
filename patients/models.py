from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام بیمار")
    age = models.PositiveIntegerField(verbose_name="سن")
    phone = models.CharField(max_length=15, blank=True, verbose_name="شماره تماس")
    national_id = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")
    gender = models.CharField(max_length=1, choices=[('M', 'مرد'), ('F', 'زن')], verbose_name="جنسیت")
    address = models.TextField(blank=True, verbose_name="آدرس")
    birth_date = models.DateField(blank=True, null=True, verbose_name="تاریخ تولد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "بیمار"
        verbose_name_plural = "بیماران"

class Service(models.Model):
    SERVICE_TYPES = [
        ('rehabilitation', 'بازتوانی'),
        ('medical', 'پزشکی'),
        ('nursing', 'پرستاری'),
        ('care', 'مراقبت'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="نوع خدمت")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    date = models.DateField(verbose_name="تاریخ خدمت")

    def __str__(self):
        return f"{self.get_service_type_display()} برای {self.patient.name}"

    class Meta:
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"