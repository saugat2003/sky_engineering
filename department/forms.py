"""Forms for creating and editing departments.
Author: Rupesh Dahal"""

from django import forms

from department.models import Department
from teams.forms import CONTROL_CLASS, TEXTAREA_CLASS


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = [
            'name',
            'head',
            'description',
            'specialisation',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'e.g. Platform Engineering',
            }),
            'head': forms.Select(attrs={'class': CONTROL_CLASS}),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'rows': 4,
                'placeholder': 'What does this department own?',
            }),
            'specialisation': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'rows': 4,
                'placeholder': 'Primary domain, capabilities, or operating focus.',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-300 text-primary focus:ring-primary',
            }),
        }
