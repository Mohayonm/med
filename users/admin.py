from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import CustomUser, Role


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("user_name", "email", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = (
        "id",
        "user_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "update_at",
    )
    search_fields = ("user_name", "email")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("user_name", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "roles")}),
    )
    add_fieldsets = (
        (None, {"fields": ("user_name", "email", "password1", "password2")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fa_name",
        "en_name",
        "description",
        "created_at",
        "update_at",
    )
    search_fields = ("en_name", "fa_name")
    list_filter = ("en_name", "fa_name")
