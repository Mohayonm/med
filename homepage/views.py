from django.shortcuts import redirect, render

def home(request):
    """صفحه اصلی سایت"""
    if request.user.is_authenticated:
        return redirect("users:dashboard")
    return render(request, "users/home.html")
