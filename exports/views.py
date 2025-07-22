from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.conf import settings
import os
from django.contrib.admin.views.decorators import staff_member_required


@login_required(login_url="/login/")
def export_dashboard(request):
    """صفحه اصلی گزارش‌گیری و خروجی"""
    return render(request, "exports/export_dashboard.html", {})


@staff_member_required(login_url="/login/")
def download_database(request):
    """دانلود فایل دیتابیس SQLite
    
    این ویو فقط برای کاربران مدیر قابل دسترسی است.
    """
    db_path = settings.DATABASES['default']['NAME']
    if os.path.exists(db_path):
        response = FileResponse(open(db_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="database-backup.sqlite3"'
        return response
    return render(request, "exports/export_dashboard.html", 
                 {'error': 'فایل دیتابیس یافت نشد'})
