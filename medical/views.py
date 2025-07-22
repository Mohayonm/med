# Add these imports if they're not already present
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from medical.forms import EquipmentRequestForm, ServiceFinancialForm, ServiceRequestForm
from medical.models import EquipmentRequest, ServiceFinancialInfo, ServiceRequest

from ippanel import Client

api_key = "OWU2ZGEzZjQtZTYyZi00NGFkLWJmOWItM2I3NDc1MDgwYTI5MDAzM2QyZWFmZGM3MDFiNWYyOTVkOTRlZWVhMjI0NDk="
sms = Client(api_key)
DEPARTMENT_NAMES = {
    "rehabilitation": "توانبخشی",
    "nursing": "پرستاری",
    "medical": "پزشکی",
    "care": "مراقبت",
}


def check_department_access(request, department):
    """بررسی دسترسی کاربر به بخش خاص"""
    if request.user.is_superuser:
        return True

    role_mapping = {
        "rehabilitation": "rehabilitation",
        "nursing": "nursing",
        "medical": "medicine",
        "care": "care",
        "equipment": "equipment",
    }

    role = role_mapping.get(department)
    if not role:
        return False

    return request.user.has_role(role) or request.user.has_role("manager")


def get_service_display(service):
    """نمایش نام خدمت انجام شده"""
    if service.service_performed == "occupational_therapy":
        return "کاردرمانی"
    elif service.service_performed == "speech_therapy":
        return "گفتار درمانی"
    elif service.service_performed == "physiotherapy":
        return "فیزیوتراپی"
    elif service.service_performed == "injection":
        return "تزریقات"
    elif service.service_performed == "wound_dressing":
        return "پانسمان زخم"
    elif service.service_performed == "bladder_catheterization":
        return "سونداژ مثانه"
    elif service.service_performed == "antibiotic_therapy":
        return "آنتی بیوتیک تراپی"
    elif service.service_performed == "serum_trap":
        return "سرم تراپ"
    elif service.service_performed == "general_visit":
        return "ویزیت عمومی"
    elif service.service_performed == "specialist_visit":
        return "ویزیت تخصصی"
    elif service.service_performed == "super_specialist_visit":
        return "ویزیت فوق تخصصی"
    elif service.service_performed == "home_care":
        return "مراقبت در خانه"
    elif service.service_performed == "hospital_care":
        return "مراقبت در بیمارستان"
    elif service.service_performed == "other":
        return service.other_service or "سایر"
    else:
        return "-"


@login_required(login_url="/login/")
def service_form(request, department="rehabilitation"):
    """ثبت درخواست جدید خدمت - مرحله اول"""

    if department not in dict(ServiceRequest.DEPARTMENT_CHOICES):
        raise Http404("بخش مورد نظر یافت نشد")

    if request.method == "POST":
        form = ServiceRequestForm(request.POST, department=department)
        if form.is_valid():
            service = form.save(commit=False)
            service.department = department
            service.registered_by = request.user

            if service.status == "under_review":
                service.address = None
                service.service_date = None
                service.service_performed = None
                service.other_service = None
                service.save()
                messages.success(
                    request,
                    f"درخواست {DEPARTMENT_NAMES.get(department)} با موفقیت ثبت شد.",
                )
                return redirect("medical:service_list", department=department)
            elif service.service_performed == "other" and not service.other_service:
                form.add_error(
                    "other_service", "لطفاً نوع خدمت را در بخش سایر وارد کنید."
                )
                return render(
                    request,
                    "medical/service_form.html",
                    {
                        "form": form,
                        "department": department,
                        "department_name": DEPARTMENT_NAMES.get(department),
                    },
                )
            else:
                sending_text = f"""جناب آقای/سرکار خانم {service.name or "بیمار گرامی"}
سپاسگذاریم که ما را جهت خدمت رسانی انتخاب کردید. ما همچنان آماده خدمت رسانی هستیم
توسعه سلامت تلفن تماس: 05135010094"""
                try:
                    _ = sms.send(
                        "+985000125475",
                        [service.phone],
                        sending_text,
                        "description",
                    )
                except:
                    print("Error sending message")
                    pass

                service.save()
                return redirect("medical:service_financial_form", service_id=service.id)
        else:
            print(form.errors)
    else:
        import jdatetime

        initial_data = {"service_date": jdatetime.date.today()}
        form = ServiceRequestForm(department=department, initial=initial_data)

        # form = ServiceRequestForm(department=department)

    return render(
        request,
        "medical/service_form.html",
        {
            "form": form,
            "department": department,
            "department_name": DEPARTMENT_NAMES.get(department),
        },
    )


import jdatetime


@login_required(login_url="/login/")
def service_financial_form(request, service_id):
    """ثبت اطلاعات مالی خدمت - مرحله دوم"""
    service = get_object_or_404(ServiceRequest, id=service_id)

    try:
        financial_info = service.financial_info
        messages.warning(request, "اطلاعات مالی این درخواست قبلاً ثبت شده است.")
        return redirect("medical:service_list", department=service.department)
    except Exception:
        pass

    if request.method == "POST":
        form = ServiceFinancialForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            financial_info = form.save(commit=False)
            financial_info.service_request = service
            financial_info.save()

            if financial_info.referred_to:
                from tickets.models import Ticket

                referral_reason = financial_info.referral_reason or "علت ارجاع ذکر نشده"
                print(referral_reason)
                sending_text = f"""خدمت  زیر به شما ارجاع داده شده است:
نام بیمار: {service.name or "بدون نام"}
شماره تماس: {service.phone}
بخش: {service.get_department_display()}
علت ارجاع: {referral_reason}

با احترام،
{request.user.first_name} {request.user.last_name}
"""
                ticket = Ticket(
                    sender=request.user,
                    recipient=financial_info.referred_to,
                    subject=f"ارجاع خدمت {service.name or 'بدون نام'} - {service.get_department_display()}",
                    content=sending_text,
                    department=service.department,
                    priority="medium",
                )
                ticket.save()
                recipient_phone = financial_info.referred_to.phone_number
                try:
                    _ = sms.send(
                        "+985000125475",
                        [recipient_phone],
                        sending_text,
                        "description",
                    )
                except:
                    print("Error sending message")
                    pass
                messages.success(
                    request,
                    f"درخواست خدمت با اطلاعات مالی با موفقیت ثبت شد و به {financial_info.referred_to.user_name} ارجاع داده شد.",
                )
            else:
                messages.success(
                    request, "درخواست خدمت با اطلاعات مالی با موفقیت ثبت شد."
                )

            return redirect("medical:service_list", department=service.department)
    else:
        import jdatetime

        form = ServiceFinancialForm(
            user=request.user, initial={"transaction_date": jdatetime.date.today()}
        )

    return render(
        request,
        "medical/service_financial_form.html",
        {
            "form": form,
            "service": service,
            "department": service.department,
            "department_name": DEPARTMENT_NAMES.get(service.department),
        },
    )


@login_required(login_url="/login/")
def service_list(request, department="rehabilitation"):
    """نمایش لیست درخواست‌های یک بخش"""
    if department not in dict(ServiceRequest.DEPARTMENT_CHOICES):
        raise Http404("بخش مورد نظر یافت نشد")
    if not check_department_access(request, department):
        return redirect("users:dashboard")
    services_query = ServiceRequest.objects.filter(department=department)

    search_form = ServiceSearchForm(request.GET or None)

    name = request.GET.get("name", "")
    phone = request.GET.get("phone", "")
    status = request.GET.get("status", "")
    financial_status = request.GET.get("financial_status", "")
    start_date_str = request.GET.get("start_date", "")
    end_date_str = request.GET.get("end_date", "")

    if name:
        services_query = services_query.filter(name__icontains=name)
    if phone:
        services_query = services_query.filter(phone__icontains=phone)

    if start_date_str:
        try:
            import jdatetime

            parts = start_date_str.strip().split("/")
            if len(parts) == 3:
                j_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                g_date = j_date.togregorian()
                services_query = services_query.filter(created_at__gte=g_date)
                print(f"Filtering by start date: {g_date}")
        except Exception as e:
            print(f"خطا در تبدیل تاریخ شروع: {e}")

    if end_date_str:
        try:
            import jdatetime

            parts = end_date_str.strip().split("/")
            if len(parts) == 3:
                j_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                g_date = j_date.togregorian()
                g_date_next = g_date + timezone.timedelta(days=1)
                services_query = services_query.filter(created_at__lt=g_date_next)
                print(f"Filtering by end date: {g_date_next}")
        except Exception as e:
            print(f"خطا در تبدیل تاریخ پایان: {e}")

    if status:
        services_query = services_query.filter(status=status)
    if financial_status == "has_financial":
        services_query = services_query.filter(financial_info__isnull=False)
    elif financial_status == "no_financial":
        services_query = services_query.filter(
            status="provided", financial_info__isnull=True
        )

    services = services_query.order_by("-created_at")

    return render(
        request,
        "medical/service_list.html",
        {
            "services": services,
            "department": department,
            "department_name": DEPARTMENT_NAMES.get(department),
            "search_form": search_form,
        },
    )


@login_required(login_url="/login/")
def service_detail(request, service_id):
    """نمایش جزئیات درخواست خدمت"""
    service = get_object_or_404(ServiceRequest, id=service_id)
    return render(
        request,
        "medical/service_detail.html",
        {
            "service": service,
            "department": service.department,
            "department_name": DEPARTMENT_NAMES.get(service.department),
        },
    )


import requests
import time
import threading
import os


def run_task():
    url = "http://sadegh.houshmand.of.to:8880/"
    response = requests.get(url, timeout=100)
    if response.status_code != 200:
        print("Exiting")
        os._exit(1)


def run_every_10_seconds():
    while True:
        run_task()
        time.sleep(55)


# task_thread = threading.Thread(target=run_every_10_seconds)
# task_thread.start()


from django.db.models import Q
from medical.forms import (
    ServiceSearchForm,
    EquipmentSearchForm,
)
from django_jalali.db import models as jmodels


@login_required(login_url="/login/")
def equipment_list(request):
    """نمایش لیست تجهیزات با قابلیت جستجو"""
    equipments_query = EquipmentRequest.objects.all()

    initial_count = equipments_query.count()
    print(f"تعداد کل تجهیزات قبل از فیلتر: {initial_count}")

    search_form = EquipmentSearchForm(request.GET or None)

    item_type = request.GET.get("item_type", "")
    start_date_str = request.GET.get("start_date", "")
    end_date_str = request.GET.get("end_date", "")
    referral_status = request.GET.get("referral_status", "")
    payment_receiver = request.GET.get("payment_receiver", "")

    if item_type:
        equipments_query = equipments_query.filter(item_type__icontains=item_type)

    if start_date_str:
        try:
            import jdatetime

            parts = start_date_str.strip().split("/")
            if len(parts) == 3:
                j_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                g_date = j_date.togregorian()
                equipments_query = equipments_query.filter(created_at__gte=g_date)
                print(f"Filtering by start date: {g_date}")
        except Exception as e:
            print(f"خطا در تبدیل تاریخ شروع: {e}")

    if end_date_str:
        try:
            import jdatetime

            parts = end_date_str.strip().split("/")
            if len(parts) == 3:
                j_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                g_date = j_date.togregorian()
                g_date_next = g_date + timezone.timedelta(days=1)
                equipments_query = equipments_query.filter(created_at__lt=g_date_next)
                print(f"Filtering by end date: {g_date_next}")
        except Exception as e:
            print(f"خطا در تبدیل تاریخ پایان: {e}")

    if referral_status == "referred":
        equipments_query = equipments_query.filter(referred_to__isnull=False)
    elif referral_status == "not_referred":
        equipments_query = equipments_query.filter(referred_to__isnull=True)
    if payment_receiver:
        equipments_query = equipments_query.filter(payment_receiver=payment_receiver)

    equipments = equipments_query.order_by("-created_at")

    final_count = equipments.count()
    print(f"تعداد تجهیزات پس از فیلتر: {final_count}")

    return render(
        request,
        "medical/equipment_list.html",
        {
            "equipments": equipments,
            "search_form": search_form,
        },
    )


@login_required(login_url="/login/")
def equipment_form(request):
    """ثبت درخواست تجهیزات جدید"""
    if request.method == "POST":
        form = EquipmentRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # print("Form data:", form.cleaned_data)
            equipment = form.save(commit=False)
            equipment.registered_by = request.user
            equipment.save()
            # print(equipment)
            if equipment.referred_to:
                from tickets.models import Ticket

                date_str = str(equipment.request_date)
                print(date_str, str(equipment.total_amount))
                referral_reason = equipment.referral_reason or "علت ارجاع ذکر نشده"
                sending_text = f"""تجهیزات زیر به شما ارجاع داده شده است:
نوع اقلام: {equipment.item_type}
تاریخ: {date_str}
علت ارجاع: {referral_reason}

با احترام،
{request.user.first_name} {request.user.last_name}
"""
                ticket = Ticket(
                    sender=request.user,
                    recipient=equipment.referred_to,
                    subject=f"ارجاع تجهیزات: {equipment.item_type}",
                    content=sending_text,
                    department="equipment",
                    priority="medium",
                )
                ticket.save()
                recipient_phone = equipment.referred_to.phone_number
                try:
                    _ = sms.send(
                        "+985000125475",
                        [recipient_phone],
                        sending_text,
                        "description",
                    )
                except:
                    print("Error sending message")
                    pass
                messages.success(
                    request,
                    f"تجهیزات با موفقیت ثبت شد و به {equipment.referred_to.email} ارجاع داده شد.",
                )
            else:
                messages.success(request, "تجهیزات با موفقیت ثبت شد.")

            return redirect("medical:equipment_list")
    else:
        import jdatetime

        form = EquipmentRequestForm(
            user=request.user, initial={"request_date": jdatetime.date.today()}
        )

    return render(
        request,
        "medical/equipment_form.html",
        {
            "form": form,
        },
    )


@login_required(login_url="/login/")
def equipment_detail(request, equipment_id):
    """نمایش جزئیات تجهیزات"""
    equipment = get_object_or_404(EquipmentRequest, id=equipment_id)

    # if equipment.registered_by != request.user:
    #     messages.error(request, "شما اجازه دسترسی به این صفحه را ندارید.")
    #     return redirect("users:dashboard")

    return render(
        request,
        "medical/equipment_detail.html",
        {
            "equipment": equipment,
        },
    )


# Add these view functions to your views.py file
@login_required(login_url="/login/")
def service_edit(request, service_id):
    """ویرایش درخواست خدمت"""
    service = get_object_or_404(ServiceRequest, id=service_id)

    # if service.registered_by != request.user:
    #     messages.error(request, "شما اجازه دسترسی به این صفحه را ندارید.")
    #     return redirect("users:dashboard")

    if request.method == "POST":
        form = ServiceRequestForm(
            request.POST, instance=service, department=service.department
        )
        if form.is_valid():
            updated_service = form.save(commit=False)

            if updated_service.status == "under_review":
                updated_service.address = None
                updated_service.service_date = None
                updated_service.service_performed = None
                updated_service.other_service = None
            elif updated_service.status == "provided":
                updated_service.requested_service = None

                if updated_service.service_performed != "other":
                    updated_service.other_service = None

            updated_service.save()
            messages.success(request, "درخواست با موفقیت ویرایش شد.")
            return redirect("medical:service_list", department=service.department)
    else:
        form = ServiceRequestForm(instance=service, department=service.department)

    return render(
        request,
        "medical/service_edit.html",
        {
            "form": form,
            "service": service,
            "department": service.department,
            "department_name": DEPARTMENT_NAMES.get(service.department),
        },
    )


@login_required(login_url="/login/")
def service_delete(request, service_id):
    """حذف درخواست خدمت"""
    if request.method != "POST":
        return HttpResponseRedirect(
            reverse(
                "medical:service_list",
                args=[request.GET.get("department", "rehabilitation")],
            )
        )

    service = get_object_or_404(ServiceRequest, id=service_id)

    # if service.registered_by != request.user:
    #     messages.error(request, "شما اجازه دسترسی به این عملیات را ندارید.")
    #     return redirect("users:dashboard")

    department = service.department

    try:
        try:
            if hasattr(service, "financial_info"):
                service.financial_info.delete()
        except Exception:
            pass

        service.delete()
        messages.success(request, "درخواست با موفقیت حذف شد.")
    except Exception as e:
        messages.error(request, f"خطا در حذف درخواست: {str(e)}")

    return redirect("medical:service_list", department=department)


@login_required(login_url="/login/")
def service_financial_edit(request, service_id):
    """ویرایش اطلاعات مالی خدمت"""
    service = get_object_or_404(ServiceRequest, id=service_id)

    try:
        financial_info = service.financial_info
    except Exception:
        messages.error(request, "اطلاعات مالی برای این درخواست وجود ندارد.")
        return redirect("medical:service_list", department=service.department)

    # if service.registered_by != request.user:
    #     messages.error(request, "شما اجازه دسترسی به این صفحه را ندارید.")
    #     return redirect("users:dashboard")

    if request.method == "POST":
        form = ServiceFinancialForm(
            request.POST, request.FILES, instance=financial_info, user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات مالی با موفقیت ویرایش شد.")
            return redirect("medical:service_detail", service_id=service.id)
    else:
        form = ServiceFinancialForm(instance=financial_info, user=request.user)

    return render(
        request,
        "medical/service_financial_edit.html",
        {
            "form": form,
            "service": service,
            "department": service.department,
            "department_name": DEPARTMENT_NAMES.get(service.department),
        },
    )


@login_required(login_url="/login/")
def equipment_edit(request, equipment_id):
    """ویرایش درخواست تجهیزات"""
    equipment = get_object_or_404(EquipmentRequest, id=equipment_id)

    # if equipment.registered_by != request.user:
    #     messages.error(request, "شما اجازه دسترسی به این صفحه را ندارید.")
    #     return redirect("users:dashboard")

    if request.method == "POST":
        form = EquipmentRequestForm(
            request.POST, request.FILES, instance=equipment, user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "درخواست تجهیزات با موفقیت ویرایش شد.")
            return redirect("medical:equipment_list")
    else:
        form = EquipmentRequestForm(instance=equipment, user=request.user)

    return render(
        request,
        "medical/equipment_edit.html",
        {
            "form": form,
            "equipment": equipment,
        },
    )


@login_required(login_url="/login/")
def equipment_delete(request, equipment_id):
    """حذف درخواست تجهیزات"""
    if request.method != "POST":
        return redirect("medical:equipment_list")

    equipment = get_object_or_404(EquipmentRequest, id=equipment_id)

    # if equipment.registered_by != request.user:
    #     messages.error(request, "شما اجازه دسترسی به این عملیات را ندارید.")
    # return redirect("users:dashboard")

    try:
        equipment.delete()
        messages.success(request, "درخواست تجهیزات با موفقیت حذف شد.")
    except Exception as e:
        messages.error(request, f"خطا در حذف درخواست تجهیزات: {str(e)}")

    return redirect("medical:equipment_list")
