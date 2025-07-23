from django.shortcuts import redirect, render

def home(request):
    """صفحه اصلی سایت"""
    if request.user.is_authenticated:
        return redirect("users:dashboard")
    return redirect("patients:patient_list")