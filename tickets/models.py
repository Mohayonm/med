from django.db import models


from django.utils.translation import gettext_lazy as _

from utils.models import BaseModel
from users.models import CustomUser


class Ticket(BaseModel):
    """
    مدل تیکت برای ارجاع کارها بین کاربران
    """

    PRIORITY_CHOICES = [
        ("low", "کم"),
        ("medium", "متوسط"),
        ("high", "زیاد"),
        ("urgent", "فوری"),
    ]

    STATUS_CHOICES = [
        ("open", "باز"),
        ("in_progress", "در حال بررسی"),
        ("closed", "بسته"),
    ]

    DEPARTMENT_CHOICES = [
        ("rehabilitation", "توانبخشی"),
        ("nursing", "پرستاری"),
        ("medical", "پزشکی"),
        ("care", "مراقبت"),
        ("equipment", "تجهیزات"),
        ("admin", "مدیریت"),
    ]

    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sent_tickets",
        verbose_name=_("فرستنده"),
    )
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="received_tickets",
        verbose_name=_("گیرنده"),
    )
    subject = models.CharField(_("موضوع"), max_length=100)
    content = models.TextField(_("متن پیام"))
    priority = models.CharField(
        _("اولویت"), max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    department = models.CharField(
        _("بخش مربوطه"), max_length=20, choices=DEPARTMENT_CHOICES
    )
    status = models.CharField(
        _("وضعیت"), max_length=15, choices=STATUS_CHOICES, default="open"
    )

    objects = models.Manager()

    class Meta:
        verbose_name = _("تیکت")
        verbose_name_plural = _("تیکت‌ها")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.status}"

