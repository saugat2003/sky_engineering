from django import forms
from django.contrib.auth.models import User


class MessageComposeForm(forms.Form):
    to = forms.CharField(label="To", max_length=150)
    subject = forms.CharField(label="Subject", max_length=255, required=False)
    body = forms.CharField(label="Body", widget=forms.Textarea)

    def clean_to(self):
        raw = (self.cleaned_data.get("to") or "").strip()
        if not raw:
            raise forms.ValidationError("Recipient is required.")

        try:
            user = User.objects.get(username__iexact=raw)
            return user
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(email__iexact=raw)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError("No user found with that username/email.")


class MessageReplyForm(forms.Form):
    body = forms.CharField(label="Body", widget=forms.Textarea)
