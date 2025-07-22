from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """بررسی اینکه آیا کاربر نقش مشخص شده را دارد یا خیر"""
    return user.has_role(role_name)