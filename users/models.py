"""
This file provide CustomUser model for users app
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import CustomUserManager
from utils.models import BaseModel


class Role(BaseModel):
    """
    Custom role model for fine-grained access control.
    """

    fa_name = models.CharField(_("fa name"), max_length=50, unique=True)
    en_name = models.CharField(_("en name"), max_length=50, unique=True)
    description = models.TextField(_("description"), blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        return f"{self.fa_name} - {self.en_name}"


class CustomUser(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom user model that supports email as the unique identifier.
    """

    roles = models.ManyToManyField(
        Role, verbose_name=_("roles"), blank=True, related_name="users"
    )

    user_name = models.CharField(
        _("user_name"),
        max_length=30,
        unique=True,
        validators=[MinLengthValidator(5)],
    )
    email = models.EmailField(_("email address"), unique=True, blank=True, null=True)
    phone_number = models.CharField(
        _("phone number"), max_length=13, unique=True, blank=True, null=True
    )
    first_name = models.CharField(_("first name"), max_length=30)
    last_name = models.CharField(_("last name"), max_length=30)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without explicitly assigning them."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts. And also used for email verification."
        ),
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True,
        verbose_name=_("profile image"),
    )
    objects = CustomUserManager()

    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class for the CustomUser
        """

        verbose_name = _("user")
        verbose_name_plural = _("users")
        constraints = [
            models.UniqueConstraint(
                fields=["user_name", "email"], name="unique_user_email"
            )
        ]

    def has_role(self, role_name):
        # pylint: disable=no-member
        return self.roles.filter(en_name=role_name).exists()

    def __str__(self) -> str:
        return f"{self.user_name} - {self.email}"
