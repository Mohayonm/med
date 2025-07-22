from django import template
from django.utils import timezone
import jdatetime

register = template.Library()


@register.filter(name="to_jalali")
def to_jalali(value):
    if value:
        return jdatetime.datetime.fromgregorian(datetime=value).strftime("%Y/%m/%d")
    return ""


@register.filter(name="format_currency")
def format_currency(value):
    """فرمت‌دهی عدد به صورت سه رقم سه رقم جدا شده با ویرگول"""
    if value is None or value == "":
        return "0"
    try:
        num = int(value)
        return f"{num:,}"
    except (ValueError, TypeError):
        return value
