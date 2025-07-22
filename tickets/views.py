from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from tickets.forms import (
    TicketForm,
)
from tickets.models import Ticket
from users.models import CustomUser

from ippanel import Client

api_key = "OWU2ZGEzZjQtZTYyZi00NGFkLWJmOWItM2I3NDc1MDgwYTI5MDAzM2QyZWFmZGM3MDFiNWYyOTVkOTRlZWVhMjI0NDk="
sms = Client(api_key)


@login_required(login_url="/login/")
def create_ticket(request):
    """ایجاد تیکت جدید و ارسال پیامک به گیرنده"""
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.sender = request.user
            ticket.save()
            messages.success(request, "تیکت با موفقیت ارسال شد.")

            try:
                recipient = ticket.recipient
                sender_name = (
                    f"{ticket.sender.first_name} {ticket.sender.last_name}"
                    if ticket.sender.first_name and ticket.sender.last_name
                    else ticket.sender.user_name
                )

                if recipient.phone_number:
                    message_body = f"سلام {recipient.first_name} {recipient.last_name} عزیز\nتیکت جدیدی برای شما ثبت شد\nموضوع: {ticket.subject}\nفرستنده: {sender_name}"

                    sender_number = "+985000125475"

                    sms_summary = f"تیکت جدید: {ticket.subject}"

                    response = sms.send(
                        sender_number,
                        [recipient.phone_number],
                        message_body,
                        summary=sms_summary,
                    )
                    print(f"SMS Send Response for ticket {ticket.id}: {response}")
                    messages.info(request, f"پیامک اطلاع‌رسانی ارسال شد.")

                else:
                    messages.warning(
                        request,
                        f"گیرنده ({recipient.user_name}) شماره تلفن ثبت شده ندارد. پیامک ارسال نشد.",
                    )

            except Exception as e:
                messages.error(request, f"خطا در ارسال پیامک اطلاع‌رسانی: {e}")
                print(f"ERROR sending SMS for ticket {ticket.id}: {e}")

            return redirect("tickets:ticket_sent")
        else:
            messages.error(request, "خطا در فرم. لطفا اطلاعات وارد شده را بررسی کنید.")
    else:
        form = TicketForm()
        form.fields["recipient"].queryset = CustomUser.objects.filter(
            is_active=True
        ).exclude(id=request.user.id)

    return render(request, "tickets/create_ticket.html", {"form": form})


@login_required(login_url="/login/")
def ticket_inbox(request):
    """نمایش تیکت‌های دریافتی"""
    tickets = Ticket.objects.filter(recipient=request.user)
    return render(request, "tickets/ticket_inbox.html", {"tickets": tickets})


@login_required(login_url="/login/")
def ticket_sent(request):
    """نمایش تیکت‌های ارسالی"""
    tickets = Ticket.objects.filter(sender=request.user)
    return render(request, "tickets/ticket_sent.html", {"tickets": tickets})


@login_required(login_url="/login/")
def ticket_detail(request, ticket_id):
    """نمایش جزئیات یک تیکت"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if (
        request.user != ticket.sender
        and request.user != ticket.recipient
        and not request.user.is_superuser
    ):
        messages.error(request, "شما اجازه دسترسی به این تیکت را ندارید.")
        return redirect("users:dashboard")

    if request.user == ticket.recipient and ticket.status == "pending":
        ticket.status = "read"
        ticket.save()

    return render(request, "tickets/ticket_detail.html", {"ticket": ticket})


@login_required(login_url="/login/")
def update_ticket_status(request, ticket_id):
    """تغییر وضعیت تیکت (AJAX)"""
    if request.method == "POST" and request.is_ajax():
        ticket = get_object_or_404(Ticket, id=ticket_id)

        if request.user != ticket.recipient:
            return JsonResponse(
                {"success": False, "error": "شما اجازه این عملیات را ندارید."}
            )

        new_status = request.POST.get("status")
        if new_status in [s[0] for s in Ticket.STATUS_CHOICES]:
            ticket.status = new_status
            ticket.save()
            return JsonResponse(
                {"success": True, "status_display": ticket.get_status_display()}
            )
        return JsonResponse({"success": False, "error": "وضعیت نامعتبر"})

    return JsonResponse({"success": False, "error": "درخواست نامعتبر"})


from django.contrib.auth.decorators import user_passes_test


def is_superuser(user):
    return user.is_superuser


@login_required(login_url="/login/")
def admin_all_tickets(request):
    """نمایش تمامی تیکت‌های سیستم برای ادمین"""
    tickets = Ticket.objects.all()

    status_filter = request.GET.get("status", "")
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    department_filter = request.GET.get("department", "")
    if department_filter:
        tickets = tickets.filter(department=department_filter)

    tickets = tickets.order_by("-created_at")

    return render(
        request,
        "tickets/admin_all_tickets.html",
        {
            "tickets": tickets,
            "status_choices": Ticket.STATUS_CHOICES,
            "department_choices": Ticket.DEPARTMENT_CHOICES,
            "current_status": status_filter,
            "current_department": department_filter,
        },
    )
