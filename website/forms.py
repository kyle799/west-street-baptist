from django import forms

from .models import FormSubmission


class _SubmissionForm(forms.ModelForm):
    """
    Base for the contact + prayer forms.

    Validation mirrors online-sermon/internal/feedback/handler.go:
    message is required (<= 4000 chars), name/email/phone optional and
    trimmed, source_path must start with "/" or is dropped. A honeypot
    field ("company") catches naive bots.
    """

    # Honeypot — real users never see/fill this. Bots that fill every input
    # trip it and the submission is silently rejected.
    company = forms.CharField(required=False, widget=forms.HiddenInput, label="")

    kind = FormSubmission.Kind.CONTACT  # overridden by subclasses

    class Meta:
        model = FormSubmission
        fields = ["name", "email", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "message": forms.Textarea(attrs={"rows": 6, "maxlength": 4000}),
        }

    def __init__(self, *args, source_path: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._source_path = source_path
        self.fields["message"].required = True
        for name in ("name", "email", "phone"):
            self.fields[name].required = False

    def clean_company(self):
        # If the honeypot is filled, raise a generic error to abort the save.
        if self.cleaned_data.get("company"):
            raise forms.ValidationError("Spam detected.")
        return ""

    def _clean_str(self, name):
        return (self.cleaned_data.get(name) or "").strip()

    def clean_name(self):
        return self._clean_str("name")

    def clean_phone(self):
        return self._clean_str("phone")

    def clean_message(self):
        msg = self._clean_str("message")
        if not msg:
            raise forms.ValidationError("Please enter a message.")
        if len(msg) > 4000:
            raise forms.ValidationError("Message is too long (4000 characters max).")
        return msg

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.kind = self.kind
        sp = (self._source_path or "").strip()
        obj.source_path = sp[:2000] if sp.startswith("/") else ""
        if commit:
            obj.save()
        return obj


class ContactForm(_SubmissionForm):
    kind = FormSubmission.Kind.CONTACT


class PrayerForm(_SubmissionForm):
    kind = FormSubmission.Kind.PRAYER
