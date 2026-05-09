"""Forms for account registration.
Author: Saugat Bhattarai and Rupesh Dahal
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password]
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]

    def clean(self):
        """Validate matching passwords.

        Returns:
            dict: Cleaned form data.

        Raises:
            ValidationError: When password and confirmation do not match.
        """
        cleaned_data = super().clean()

        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        """Create a new user with a hashed password.

        Args:
            commit: Whether to persist the user to the database.

        Returns:
            User: The created user instance.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user