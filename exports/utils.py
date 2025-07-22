import xlwt
from django.http import HttpResponse
from django.utils import timezone
from medical.models import ServiceRequest, EquipmentRequest, ServiceFinancialInfo
from tickets.models import Ticket

"""
Utility functions for exporting data to Excel files.
This module centralizes all export functionality for better organization.
"""


def export_services_excel(request, department=None):
    """Export services data to Excel file"""
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        f'attachment; filename="services_{department or "all"}_{timezone.now().strftime("%Y%m%d%H%M%S")}.xls"'
    )

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet(f"خدمات {get_department_name(department)}")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [
        "شناسه",
        "نام بیمار",
        "شماره تماس",
        "بخش",
        "وضعیت",
        "خدمت مورد نیاز",
        "خدمت انجام شده",
        "آدرس",
        "تاریخ ارائه خدمت",
        "سایر خدمات",
        "نام معرف",  # Add the referrer name column here
        "ثبت کننده",
        "تاریخ ثبت",
    ]

    # Add financial info columns if admin
    if request.user.is_superuser:
        columns.extend(
            [
                "کارشناس/پزشک",
                "مبلغ کل (تومان)",
                "مبلغ مصرفی (تومان)",
                "سهم پزشک (تومان)",
                "سهم مرکز (تومان)",
                "سهم معرف (تومان)",
                "نوع مصرفی",
                "تاریخ تراکنش",
                "ارجاع به",
            ]
        )

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # Get all services or filter by department
    services = ServiceRequest.objects.all()
    if department:
        services = services.filter(department=department)

    # If not admin, only show current user's services
    if not request.user.is_superuser:
        services = services.filter(registered_by=request.user)

    for service in services:
        row_num += 1

        # Basic service data
        row = [
            service.id,
            service.name or "",
            service.phone,
            get_department_name(service.department),
            get_status_name(service.status),
            service.requested_service or "",
            get_service_name(service.service_performed)
            if service.service_performed
            else "",
            service.address or "",
            str(service.service_date) if service.service_date else "",
            service.other_service or "",
            service.referrer_name or "",  # Add the referrer name data here
            f"{service.registered_by.first_name} {service.registered_by.last_name}",
            service.created_at.strftime("%Y-%m-%d %H:%M"),
        ]

        # Add financial info if admin and if financial info exists
        if request.user.is_superuser:
            try:
                financial = service.financial_info
                row.extend(
                    [
                        financial.specialist_name,
                        financial.total_amount,
                        financial.consumed_amount,
                        financial.doctor_share,
                        financial.center_share,
                        financial.consume_share,
                        financial.consumed_type or "",
                        str(financial.transaction_date)
                        if financial.transaction_date
                        else "",
                        f"{financial.referred_to.first_name} {financial.referred_to.last_name}"
                        if financial.referred_to
                        else "",
                    ]
                )
            except Exception:
                row.extend(["", 0, 0, 0, 0, 0, "", "", ""])

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def export_equipment_excel(request):
    """Export equipment data to Excel file"""
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        f'attachment; filename="equipment_{timezone.now().strftime("%Y%m%d%H%M%S")}.xls"'
    )

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("تجهیزات")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [
        "شناسه",
        "نوع اقلام",
        "تعداد",
        "مبلغ دریافتی (تومان)",
        "تاریخ",
        "مصرف",
        "حق السهم مرکز (تومان)",
        "حق السهم معرف (تومان)",
        "نام معرف",  # Add the referrer name column here
        "ثبت کننده",
        "ارجاع به",
        "تاریخ ثبت",
    ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    equipments = EquipmentRequest.objects.all()

    # If not admin, only show current user's equipment requests
    if not request.user.is_superuser:
        equipments = equipments.filter(registered_by=request.user)

    for equipment in equipments:
        row_num += 1
        row = [
            equipment.id,
            equipment.item_type,
            equipment.quantity,
            equipment.total_amount,
            str(equipment.request_date) if equipment.request_date else "",
            equipment.consumption or "",
            equipment.center_share,
            equipment.consume_share,
            equipment.referrer_name or "",  # Add the referrer name data here
            f"{equipment.registered_by.first_name} {equipment.registered_by.last_name}",
            f"{equipment.referred_to.first_name} {equipment.referred_to.last_name}"
            if equipment.referred_to
            else "",
            equipment.created_at.strftime("%Y-%m-%d %H:%M"),
        ]

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def export_tickets_excel(request):
    """Export tickets data to Excel file"""
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        f'attachment; filename="tickets_{timezone.now().strftime("%Y%m%d%H%M%S")}.xls"'
    )

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("تیکت ها")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [
        "شناسه",
        "موضوع",
        "متن پیام",
        "اولویت",
        "بخش مربوطه",
        "وضعیت",
        "فرستنده",
        "گیرنده",
        "تاریخ ایجاد",
    ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    tickets = Ticket.objects.all()

    # If not admin, only show tickets sent or received by current user
    if not request.user.is_superuser:
        tickets = tickets.filter(sender=request.user) | tickets.filter(
            recipient=request.user
        )

    for ticket in tickets:
        row_num += 1
        row = [
            ticket.id,
            ticket.subject,
            ticket.content,
            get_priority_name(ticket.priority),
            get_ticket_department_name(ticket.department),
            get_ticket_status_name(ticket.status),
            f"{ticket.sender.first_name} {ticket.sender.last_name}",
            f"{ticket.recipient.first_name} {ticket.recipient.last_name}",
            ticket.created_at.strftime("%Y-%m-%d %H:%M"),
        ]

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# Helper functions for translating values to Persian
def get_department_name(department):
    """Get department name in Persian"""
    department_names = {
        "rehabilitation": "توانبخشی",
        "nursing": "پرستاری",
        "medical": "پزشکی",
        "care": "مراقبت",
        None: "همه",
    }
    return department_names.get(department, department)


def get_status_name(status):
    """Get status name in Persian"""
    status_names = {"under_review": "در دست بررسی", "provided": "منجر به خدمت"}
    return status_names.get(status, status)


def get_service_name(service_performed):
    """Get service name in Persian"""
    service_names = {
        "occupational_therapy": "کاردرمانی",
        "speech_therapy": "گفتار درمانی",
        "physiotherapy": "فیزیوتراپی",
        "injection": "تزریقات",
        "wound_dressing": "پانسمان زخم",
        "bladder_catheterization": "سونداژ مثانه",
        "antibiotic_therapy": "آنتی بیوتیک تراپی",
        "serum_trap": "سرم تراپ",
        "general_visit": "ویزیت عمومی",
        "specialist_visit": "ویزیت تخصصی",
        "super_specialist_visit": "ویزیت فوق تخصصی",
        "home_care": "مراقبت در خانه",
        "hospital_care": "مراقبت در بیمارستان",
        "other": "سایر",
    }
    return service_names.get(service_performed, service_performed)


def get_priority_name(priority):
    """Get priority name in Persian"""
    priority_names = {"low": "کم", "medium": "متوسط", "high": "زیاد", "urgent": "فوری"}
    return priority_names.get(priority, priority)


def get_ticket_department_name(department):
    """Get ticket department name in Persian"""
    department_names = {
        "rehabilitation": "توانبخشی",
        "nursing": "پرستاری",
        "medical": "پزشکی",
        "care": "مراقبت",
        "equipment": "تجهیزات",
        "admin": "مدیریت",
    }
    return department_names.get(department, department)


def get_ticket_status_name(status):
    """Get ticket status name in Persian"""
    status_names = {"open": "باز", "in_progress": "در حال بررسی", "closed": "بسته"}
    return status_names.get(status, status)
