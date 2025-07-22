from django import forms
from medical.models import ServiceRequest, ServiceFinancialInfo, EquipmentRequest
from users.models import CustomUser


class ServiceRequestForm(forms.ModelForm):
    """فرم درخواست خدمت"""

    status = forms.ChoiceField(
        choices=ServiceRequest.STATUS_CHOICES,
        label="وضعیت درخواست",
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = ServiceRequest
        fields = [
            "status",
            "name",
            "phone",
            "requested_service",
            "address",
            "service_date",
            "service_performed",
            "other_service",
            "referrer_name",
            "description",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "dir": "ltr"}),
            "requested_service": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "service_date": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "مثال: 1404/02/19"}
            ),
            "service_performed": forms.Select(attrs={"class": "form-select"}),
            "other_service": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "referrer_name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop("department", "rehabilitation")

        super().__init__(*args, **kwargs)
        print(f"Department received: '{department}'")

        if department == "rehabilitation":
            service_choices = ServiceRequest.REHABILITATION_SERVICE_CHOICES
            print("Using rehabilitation choices")
        elif department == "nursing":
            service_choices = ServiceRequest.NURSING_SERVICE_CHOICES
            print("Using nursing choices")
        elif department == "medical":
            service_choices = ServiceRequest.MEDICAL_SERVICE_CHOICES
            print("Using medical choices")
        elif department == "care":
            service_choices = ServiceRequest.CARE_SERVICE_CHOICES
            print("Using care choices")
        else:
            service_choices = ServiceRequest.REHABILITATION_SERVICE_CHOICES
            print(f"Unrecognized department, using default rehabilitation choices")

        choices = [("", "---------")] + list(service_choices)

        print(f"Choices being set: {choices}")

        self.fields["service_performed"].choices = choices

        print(
            f"Field choices after setting: {self.fields['service_performed'].choices}"
        )

        self.fields["service_performed"].validators = []


class ServiceFinancialForm(forms.ModelForm):
    """فرم اطلاعات مالی خدمت"""

    class Meta:
        model = ServiceFinancialInfo
        fields = [
            "specialist_name",
            "total_amount",
            "consumed_amount",
            "doctor_share",
            "center_share",
            "consumed_type",
            "transaction_date",
            "consume_share",
            "referred_to",
            "referral_reason",
            "description",
            "payment_receiver",
            "receipt_image",
        ]
        widgets = {
            "payment_receiver": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "specialist_name": forms.TextInput(attrs={"class": "form-control"}),
            "total_amount": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "placeholder": "مبلغ به تومان",
                }
            ),
            "consumed_amount": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "placeholder": "مبلغ به تومان",
                }
            ),
            "doctor_share": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "placeholder": "مبلغ به تومان",
                }
            ),
            "center_share": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "placeholder": "مبلغ به تومان",
                }
            ),
            "consume_share": forms.TextInput(
                attrs={
                    "class": "form-control money-input",
                    "placeholder": "مبلغ به تومان",
                }
            ),
            "consumed_type": forms.TextInput(attrs={"class": "form-control"}),
            "transaction_date": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثال: 1403/01/01",
                    "autocomplete": "off",
                }
            ),
            "referred_to": forms.Select(attrs={"class": "form-select"}),
            "referral_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "توضیح دهید چرا این درخواست ارجاع داده می‌شود",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "هرگونه توضیح اضافی در مورد این خدمت را وارد کنید",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Clean numeric fields
        numeric_fields = [
            "total_amount",
            "consumed_amount",
            "doctor_share",
            "center_share",
            "consume_share",
        ]
        for field in numeric_fields:
            if cleaned_data.get(field):
                if isinstance(cleaned_data[field], str):
                    # Remove commas and convert to integer
                    cleaned_data[field] = int(cleaned_data[field].replace(",", ""))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["referred_to"].queryset = CustomUser.objects.filter(
                is_active=True
            ).exclude(id=user.id)




class EquipmentRequestForm(forms.ModelForm):
    """فرم درخواست تجهیزات"""

    total_amount = forms.IntegerField(
        label="مبلغ دریافتی (تومان)",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control money-input", "placeholder": "مبلغ به تومان"}
        ),
    )
    center_share = forms.IntegerField(
        label="حق السهم مرکز (تومان)",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control money-input", "placeholder": "مبلغ به تومان"}
        ),
    )
    consume_share = forms.IntegerField(
        label="حق السهم مصرف (تومان)",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control money-input", "placeholder": "مبلغ به تومان"}
        ),
    )

    class Meta:
        model = EquipmentRequest
        fields = [
            "item_type",
            "payment_receiver",
            "quantity",
            "total_amount",
            "request_date",
            "center_share",
            "consume_share",
            "referred_to",
            "referrer_name",
            "referral_reason",
            "receipt_image",
            "description",
        ]
        widgets = {
            "payment_receiver": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "item_type": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "request_date": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "مثال: 1403/01/01",
                    "autocomplete": "off",
                }
            ),
            "consumption": forms.TextInput(attrs={"class": "form-control"}),
            "referrer_name": forms.TextInput(attrs={"class": "form-control"}),
            "referral_reason": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "هرگونه توضیح اضافی در مورد این تجهیزات را وارد کنید",
                }
            ),
        }

    def clean(self):
        """تمیز کردن و اعتبارسنجی داده‌ها"""
        cleaned_data = super().clean()
        for field_name in ["total_amount", "center_share", "consume_share"]:
            if field_name in cleaned_data and cleaned_data[field_name] in ["", None]:
                cleaned_data[field_name] = 0

        return cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["referred_to"].queryset = CustomUser.objects.filter(
                is_active=True
            ).exclude(id=user.id)


class ServiceSearchForm(forms.Form):
    """فرم جستجوی درخواست‌های خدمت"""

    name = forms.CharField(
        label="نام بیمار",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "جستجو بر اساس نام بیمار"}
        ),
    )
    phone = forms.CharField(
        label="شماره تلفن",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "جستجو بر اساس شماره تلفن"}
        ),
    )
    start_date = forms.CharField(
        label="از تاریخ",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control jalali-datepicker",
                "placeholder": "مثال: 1403/01/01",
                "autocomplete": "off",
            }
        ),
    )
    end_date = forms.CharField(
        label="تا تاریخ",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control jalali-datepicker",
                "placeholder": "مثال: 1403/01/30",
                "autocomplete": "off",
            }
        ),
    )
    status = forms.ChoiceField(
        label="وضعیت",
        required=False,
        choices=[
            ("", "همه"),
            ("under_review", "در دست بررسی"),
            ("provided", "منجر به خدمت"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    financial_status = forms.ChoiceField(
        label="وضعیت مالی",
        required=False,
        choices=[
            ("", "همه"),
            ("has_financial", "اطلاعات مالی ثبت شده"),
            ("no_financial", "اطلاعات مالی ثبت نشده"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class EquipmentSearchForm(forms.Form):
    """فرم جستجوی تجهیزات"""

    item_type = forms.CharField(
        label="نوع اقلام",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "جستجو بر اساس نوع اقلام"}
        ),
    )
    start_date = forms.CharField(
        label="از تاریخ",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control jalali-datepicker",
                "placeholder": "مثال: 1403/01/01",
                "autocomplete": "off",
            }
        ),
    )
    end_date = forms.CharField(
        label="تا تاریخ",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control jalali-datepicker",
                "placeholder": "مثال: 1403/01/30",
                "autocomplete": "off",
            }
        ),
    )
    referral_status = forms.ChoiceField(
        label="وضعیت ارجاع",
        required=False,
        choices=[
            ("", "همه"),
            ("referred", "ارجاع شده"),
            ("not_referred", "بدون ارجاع"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    payment_receiver = forms.ChoiceField(
        label="دریافت وجه",
        required=False,
        choices=[
            ("", "همه"),
            ("specialist", "توسط کارشناس اعزامی"),
            ("center", "توسط مرکز"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
