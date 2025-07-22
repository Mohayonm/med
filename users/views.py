from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import CustomUserCreationForm, ResetPasswordForm, UserProfileForm
from users.models import CustomUser, Role


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("users:dashboard")
        return render(request, "users/login.html", {"error": "اطلاعات به صورت نادرست وارد شده است."})
    return render(request, "users/login.html")


@login_required(login_url="/login/")
def dashboard(request):
    # TODO: print user role en_name
    # roles = list(request.user.roles.values_list("en_name", flat=True))
    # print(f"User {request.user.user_name} has roles: {roles}")

    context = {
        "is_accountant": request.user.has_role("accountant"),
        "is_secretary": request.user.has_role("secretary"),
    }
    return render(request, "users/dashboard.html", context)


def user_logout(request):
    logout(request)
    return redirect("users:login")


def superuser_required(function):
    actual_decorator = user_passes_test(lambda u: u.is_superuser, login_url="/login/")
    return actual_decorator(function)


@login_required(login_url="/login/")
@superuser_required
def user_list(request):
    """نمایش لیست کاربران برای مدیریت دسترسی‌ها"""
    users = CustomUser.objects.all().order_by("id")
    return render(request, "users/user_list.html", {"users": users})


@login_required(login_url="/login/")
@superuser_required
def user_permissions(request, user_id):
    """مدیریت دسترسی‌های یک کاربر خاص"""
    user = get_object_or_404(CustomUser, id=user_id)
    roles = Role.objects.all()

    if request.method == "POST":
        user.roles.clear()

        for role_id in request.POST.getlist("roles"):
            role = Role.objects.get(id=role_id)
            user.roles.add(role)

        user.is_staff = "is_staff" in request.POST
        user.is_superuser = "is_superuser" in request.POST
        user.save()

        messages.success(
            request, f"سطوح دسترسی {user.user_name} با موفقیت بروزرسانی شد."
        )
        return redirect("users:user_list")

    return render(
        request,
        "users/user_permissions.html",
        {
            "user": user,
            "roles": roles,
            "user_roles": user.roles.all(),
        },
    )


@login_required(login_url="/login/")
@superuser_required
def add_user(request):
    """افزودن کاربر جدید"""
    roles = Role.objects.all()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            for role_id in request.POST.getlist("roles"):
                role = Role.objects.get(id=role_id)
                user.roles.add(role)

            messages.success(request, f"کاربر {user.user_name} با موفقیت ایجاد شد.")
            return redirect("users:user_list")
    else:
        form = CustomUserCreationForm()

    return render(
        request,
        "users/add_user.html",
        {
            "form": form,
            "roles": roles,
        },
    )


@login_required(login_url="/login/")
@superuser_required
def delete_user(request, user_id):
    """حذف کاربر"""
    user = get_object_or_404(CustomUser, id=user_id)

    if user == request.user:
        messages.error(request, "شما نمی‌توانید حساب کاربری خود را حذف کنید.")
        return redirect("users:user_list")

    if request.method == "POST":
        user_name = user.user_name
        user.delete()
        messages.success(request, f"کاربر {user_name} با موفقیت حذف شد.")
        return redirect("users:user_list")

    return render(request, "users/delete_user.html", {"user": user})


@login_required(login_url="/login/")
@superuser_required
def reset_user_password(request, user_id):
    """تغییر رمز عبور کاربر توسط ادمین"""
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password1"])
            user.save()

            messages.success(
                request, f"رمز عبور کاربر {user.user_name} با موفقیت تغییر کرد."
            )
            return redirect("users:user_list")
    else:
        form = ResetPasswordForm()

    return render(
        request, "users/reset_user_password.html", {"form": form, "user": user}
    )


@login_required(login_url="/login/")
def user_profile(request):
    """نمایش و ویرایش پروفایل کاربری"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات پروفایل با موفقیت به‌روزرسانی شد.")
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)

    roles = list(request.user.roles.all())

    return render(request, "users/profile.html", {"form": form, "roles": roles})


@login_required(login_url="/login/")
def change_password(request):
    """تغییر رمز عبور توسط کاربر"""
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            request.user.set_password(new_password)
            request.user.save()
            user = authenticate(username=request.user.user_name, password=new_password)
            login(request, user)

            messages.success(request, "رمز عبور شما با موفقیت تغییر کرد.")
            return redirect("users:profile")
    else:
        form = ResetPasswordForm()

    return render(request, "users/reset_user_password.html", {"form": form})