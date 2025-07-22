from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """فرم ایجاد کاربر جدید با فیلدهای سفارشی"""

    email = forms.EmailField(
        max_length=254,
        required=False,  # Changed from True to False
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone_number = forms.CharField(
        max_length=13,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "مثال: 989123456789+"}
        ),
    )
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_superuser = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = CustomUser
        fields = (
            "user_name",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password1",
            "password2",
            "is_staff",
            "is_superuser",
        )
        widgets = {
            "user_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

        self.fields[
            "password1"
        ].help_text = (
            "رمز عبور باید حداقل 8 کاراکتر باشد و نباید خیلی ساده یا رایج باشد."
        )
        self.fields["password2"].help_text = "برای تأیید، رمز عبور را مجدداً وارد کنید."

    def clean_password2(self):
        """اعتبارسنجی و فارسی‌سازی خطاهای رمز عبور"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("رمز عبور و تأیید آن با هم مطابقت ندارند.")

        try:
            validate_password(password2, self.instance)
        except ValidationError as error:
            farsi_errors = []
            for e in error.messages:
                if "too short" in e:
                    farsi_errors.append(
                        "رمز عبور خیلی کوتاه است. باید حداقل 8 کاراکتر داشته باشد."
                    )
                elif "too common" in e:
                    farsi_errors.append("این رمز عبور خیلی رایج و ساده است.")
                elif "entirely numeric" in e:
                    farsi_errors.append("رمز عبور نمی‌تواند فقط شامل اعداد باشد.")
                else:
                    farsi_errors.append(e)

            raise ValidationError(farsi_errors)

        return password2


class ResetPasswordForm(forms.Form):
    """فرم تغییر رمز عبور توسط ادمین"""

    new_password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        strip=False,
    )

    new_password2 = forms.CharField(
        label="تأیید رمز عبور جدید",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_new_password2(self):
        """بررسی تطابق رمزهای عبور و اعتبارسنجی"""
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("رمز عبور و تأیید آن با هم مطابقت ندارند.")

        try:
            validate_password(password2)
        except ValidationError as error:
            farsi_errors = []
            for e in error.messages:
                if "too short" in e:
                    farsi_errors.append(
                        "رمز عبور خیلی کوتاه است. باید حداقل 8 کاراکتر داشته باشد."
                    )
                elif "too common" in e:
                    farsi_errors.append("این رمز عبور خیلی رایج و ساده است.")
                elif "entirely numeric" in e:
                    farsi_errors.append("رمز عبور نمی‌تواند فقط شامل اعداد باشد.")
                else:
                    farsi_errors.append(e)

            raise ValidationError(farsi_errors)

        return password2


class UserProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل کاربر"""

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "profile_image"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "profile_image": forms.FileInput(attrs={"class": "form-control"}),
        }

