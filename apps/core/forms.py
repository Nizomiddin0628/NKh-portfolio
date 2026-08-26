from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Botlar uchun tuzoq — odam bu maydonni ko'rmaydi.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Your name"), "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@company.com", "autocomplete": "email"}),
            "subject": forms.TextInput(attrs={"placeholder": _("What is this about?")}),
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": _("A few sentences are enough.")}),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError(_("Spam detected."))
        return ""

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 20:
            raise forms.ValidationError(_("Please write at least 20 characters so I can reply properly."))
        return message
