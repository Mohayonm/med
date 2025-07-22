from django import forms
from tickets.models import Ticket, CustomUser


class TicketForm(forms.ModelForm):
    """فرم ایجاد تیکت جدید"""

    recipient = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        label="گیرنده",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Ticket
        fields = ["recipient", "subject", "content", "priority", "department"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
        }
