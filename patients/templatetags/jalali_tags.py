from django import template
import jdatetime

register = template.Library()

@register.filter
def jdate(value, format_string="Y/m/d"):
    if not value:
        return ""
    try:
        # تبدیل تاریخ میلادی به شمسی
        jalali_date = jdatetime.date.fromgregorian(date=value)
        return jalali_date.strftime(format_string)
    except (TypeError, ValueError):
        return ""