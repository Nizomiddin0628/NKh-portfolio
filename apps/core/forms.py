import re

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


PHONE_CHARS = re.compile(r"^[0-9+()\-\s]{7,24}$")


class ContactForm(forms.ModelForm):
    # Botlar uchun tuzoq — odam bu maydonni ko'rmaydi.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        labels = {"name": _("Name"), "email": _("Email"), "phone": _("Phone"),
                  "subject": _("Subject"), "message": _("Message")}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Your name"), "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@company.com", "autocomplete": "email"}),
            "phone": forms.TelInput(attrs={"placeholder": "+998 90 123 45 67",
                                           "autocomplete": "tel", "inputmode": "tel"}),
            "subject": forms.TextInput(attrs={"placeholder": _("What is this about?")}),
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": _("A few sentences are enough.")}),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError(_("Spam detected."))
        return ""

    def clean_phone(self):
        """Optional. Accepts digits, spaces, +, - and brackets; 7-15 digits."""
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return ""
        digits = sum(ch.isdigit() for ch in phone)
        if not PHONE_CHARS.match(phone) or not 7 <= digits <= 15:
            raise forms.ValidationError(
                _("Enter a phone number with country code, e.g. +998 90 123 45 67."))
        return phone

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 20:
            raise forms.ValidationError(_("Please write at least 20 characters so I can reply properly."))
        return message
