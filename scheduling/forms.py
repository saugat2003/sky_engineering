"""Forms for meeting scheduling."""

from django import forms
from django.contrib.auth.models import User
from .models import Meeting, MeetingAttendee


class MeetingForm(forms.ModelForm):
    """Form for creating and editing meetings."""

    attendees = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Add Attendees',
        help_text='Select users to invite to this meeting'
    )

    class Meta:
        model = Meeting
        fields = ['title', 'description', 'scheduled_at', 'duration_minutes', 
                  'platform', 'meeting_link', 'team', 'timezone', 'recurrence']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Meeting title or subject',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add agenda or meeting details...',
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 480,
                'step': 15,
            }),
            'platform': forms.Select(attrs={
                'class': 'form-control',
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/j/...',
            }),
            'team': forms.Select(attrs={
                'class': 'form-control',
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UTC, EST, PST, etc.',
            }),
            'recurrence': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make team optional
        self.fields['team'].required = False
        # Set default values
        self.fields['timezone'].initial = 'UTC'


class MeetingAttendeeForm(forms.ModelForm):
    """Form for managing meeting attendee responses."""

    class Meta:
        model = MeetingAttendee
        fields = ['rsvp_status']
        widgets = {
            'rsvp_status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
