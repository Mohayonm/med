from django.db import models
from users.models import BaseModel, CustomUser
from django_jalali.db import models as jmodels


class ServiceRequest(BaseModel):
    """مدل درخواست خدمات پزشکی و توانبخشی"""

    STATUS_CHOICES = (
        ("under_review", "در دست بررسی"),
        ("provided", "منجر به خدمت"),
    )
    REHABILITATION_SERVICE_CHOICES = (
        ("occupational_therapy", "کاردرمانی"),
        ("speech_therapy", "گفتار درمانی"),
        ("physiotherapy", "فیزیوتراپی"),
        ("other", "سایر"),
    )

    NURSING_SERVICE_CHOICES = (
        ("injection", "تزریقات"),
        ("wound_dressing", "پانسمان زخم"),
        ("bladder_catheterization", "سونداژ مثانه"),
        ("antibiotic_therapy", "آنتی بیوتیک تراپی"),
        ("serum_trap", "سرم تراپ"),
        ("other", "سایر"),
    )

    MEDICAL_SERVICE_CHOICES = (
        ("general_visit", "ویزیت عمومی"),
        ("specialist_visit", "ویزیت تخصصی"),
        ("super_specialist_visit", "ویزیت فوق تخصصی"),
        ("other", "سایر"),
    )

    CARE_SERVICE_CHOICES = (
        ("home_care", "مراقبت در خانه"),
        ("hospital_care", "مراقبت در بیمارستان"),
        ("other", "سایر"),
    )
    DEPARTMENT_CHOICES = (
        ("rehabilitation", "توانبخشی"),
        ("nursing", "پرستاری"),
        ("medical", "پزشکی"),
        ("care", "مراقبت"),
    )

    # گزینه‌های خدمت
    SERVICE_CHOICES = (
        ("occupational_therapy", "کاردرمانی"),
        ("speech_therapy", "گفتار درمانی"),
        ("physiotherapy", "فیزیوتراپی"),
        ("injection", "تزریقات"),
        ("wound_dressing", "پانسمان زخم"),
        ("bladder_catheterization", "سونداژ مثانه"),
        ("antibiotic_therapy", "آنتی بیوتیک تراپی"),
        ("serum_trap", "سرم تراپ"),
        ("general_visit", "ویزیت عمومی"),
        ("specialist_visit", "ویزیت تخصصی"),
        ("super_specialist_visit", "ویزیت فوق تخصصی"),
        ("home_care", "مراقبت در خانه"),
        ("hospital_care", "مراقبت در بیمارستان"),
        ("other", "سایر"),
    )

    name = models.CharField("نام و نام خانوادگی", max_length=100, blank=True, null=True)
    phone = models.CharField("شماره تماس", max_length=15)
    department = models.CharField("بخش", max_length=20, choices=DEPARTMENT_CHOICES)
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES)
    requested_service = models.CharField(
        "خدمت مورد نیاز", max_length=255, blank=True, null=True
    )

    service_performed = models.CharField(
        "خدمت انجام شده", max_length=50, choices=SERVICE_CHOICES, blank=True, null=True
    )

    address = models.TextField("آدرس", blank=True, null=True)
    service_date = models.CharField(
        "تاریخ ارائه خدمت", max_length=20, blank=True, null=True
    )
    other_service = models.CharField(
        "سایر خدمات", max_length=255, blank=True, null=True
    )
    referrer_name = models.CharField("نام معرف", max_length=100, blank=True, null=True)

    # کاربر ثبت‌کننده
    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="registered_services",
        verbose_name="ثبت‌کننده",
    )
    
    description = models.TextField("توضیحات", blank=True, null=True)

    objects = jmodels.jManager()

    class Meta:
        verbose_name = "درخواست خدمت"
        verbose_name_plural = "درخواست‌های خدمت"

    def __str__(self):
        return f"{self.name or 'بدون نام'} - {self.phone}"

    def get_service_performed_display_custom(self):
        """روش جایگزین برای نمایش عنوان خدمت انجام شده"""
        choices_dict = dict(self.SERVICE_CHOICES)
        return choices_dict.get(self.service_performed, self.other_service) or "-"

    @property
    def is_financial_info_complete(self):
        """بررسی می‌کند آیا فیلدهای ضروری اطلاعات مالی پر شده‌اند یا خیر."""
        try:
            financial_info = self.financial_info

            required_fields_filled = any([
                financial_info.total_amount is not None,
                financial_info.consumed_amount is not None,
                financial_info.doctor_share is not None,
                financial_info.center_share is not None,
                financial_info.consume_share is not None,
                financial_info.consumed_type 
            ])
            return required_fields_filled
        except ServiceFinancialInfo.DoesNotExist:
            return False
        except AttributeError:
             return False


class ServiceFinancialInfo(BaseModel):
    """مدل اطلاعات مالی خدمات"""

    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="financial_info",
        verbose_name="درخواست خدمت",
    )

    specialist_name = models.CharField(
        "نام و نام خانوادگی کارشناس یا پزشک", max_length=100
    )
    total_amount = models.PositiveIntegerField(
        "مبلغ دریافتی کل (تومان)", null=True, blank=True
    )
    consumed_amount = models.PositiveIntegerField(
        "مبلغ مصرفی (تومان)", null=True, blank=True
    )
    doctor_share = models.PositiveIntegerField(
        "حق و سهم پزشک (تومان)", null=True, blank=True
    )
    consume_share = models.PositiveIntegerField(
        "حق و سهم معرف (تومان)", null=True, blank=True
    )
    center_share = models.PositiveIntegerField(
        "حق السهم مرکز (تومان)", null=True, blank=True
    )
    referral_reason = models.TextField("علت ارجاع", blank=True, null=True)

    consumed_type = models.CharField("نوع مصرفی", max_length=255, blank=True)

    transaction_date = models.CharField(
        "تاریخ تراکنش", max_length=50, blank=True, null=True
    )
    receipt_image = models.ImageField(
        "تصویر رسید", upload_to="receipts/", blank=True, null=True
    )

    referred_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referred_services",
        verbose_name="ارجاع شده به",
    )
    description = models.TextField("توضیحات", blank=True, null=True)
    PAYMENT_RECEIVER_CHOICES = (
        ("specialist", "توسط کارشناس اعزامی"),
        ("center", "توسط مرکز"),
    )
    payment_receiver = models.CharField(
        "دریافت وجه از",
        max_length=50,
        choices=PAYMENT_RECEIVER_CHOICES,
        default="center",
        null=True,
        blank=True,
    )
    objects = jmodels.jManager()

    class Meta:
        verbose_name = "اطلاعات مالی خدمت"
        verbose_name_plural = "اطلاعات مالی خدمات"

    def __str__(self):
        return f"اطلاعات مالی {self.service_request}"




class EquipmentRequest(BaseModel):
    """مدل درخواست تجهیزات"""

    item_type = models.CharField("نوع اقلام", max_length=255)

    request_date = models.CharField(
        "تاریخ", max_length=50, blank=True, null=True
    )
    consumption = models.CharField("مصرف", max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField("تعداد", null=True, blank=True)
    total_amount = models.PositiveIntegerField(
        "مبلغ دریافتی (تومان)", null=True, blank=True
    )
    center_share = models.PositiveIntegerField(
        "حق السهم مرکز (تومان)", null=True, blank=True
    )
    consume_share = models.PositiveIntegerField(
        "حق السهم مصرف (تومان)", null=True, blank=True
    )
    referrer_name = models.CharField("نام معرف", max_length=100, blank=True, null=True)
    referral_reason = models.TextField("علت ارجاع", blank=True, null=True)

    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="registered_equipments",
        verbose_name="ثبت‌کننده",
    )

    referred_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referred_equipments",
        verbose_name="ارجاع شده به",
    )
    receipt_image = models.ImageField(
        "تصویر رسید", upload_to="equipment_receipts/", blank=True, null=True
    )
    description = models.TextField("توضیحات", blank=True, null=True)
    PAYMENT_RECEIVER_CHOICES = (
        ("specialist", "توسط کارشناس اعزامی"),
        ("center", "توسط مرکز"),
    )
    payment_receiver = models.CharField(
        "دریافت وجه از",
        max_length=20,
        choices=PAYMENT_RECEIVER_CHOICES,
        default="center",
        blank=True,
        null=True,
    )
    objects = jmodels.jManager()

    class Meta:
        verbose_name = "درخواست تجهیزات"
        verbose_name_plural = "درخواست‌های تجهیزات"

    def __str__(self):
        return f"{self.item_type} - {self.quantity} عدد"
