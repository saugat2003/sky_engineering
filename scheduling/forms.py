"""Forms for meeting scheduling."""

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re

from .models import Meeting, MeetingAttendee


class MeetingForm(forms.ModelForm):
    """Form for creating and editing meetings with validation."""

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
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
                'placeholder': 'Meeting title or subject',
            }),
            'description': forms.Textarea(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
                'rows': 4,
                'placeholder': 'Add agenda or meeting details...',
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
                'type': 'datetime-local',
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
                'min': 15,
                'max': 480,
                'step': 15,
            }),
            'platform': forms.Select(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
                'placeholder': 'https://zoom.us/j/... (required for remote meetings)',
            }),
            'team': forms.Select(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
                'placeholder': 'UTC, EST, PST, etc.',
            }),
            'recurrence': forms.Select(attrs={
                'class': 'px-3 py-2 border border-gray-200 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-950 dark:text-white dark:border-gray-800',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make team optional
        self.fields['team'].required = False
        if self.instance and self.instance.pk:
            self.fields['attendees'].initial = self.instance.attendees.values_list('user_id', flat=True)
        else:
            self.fields['timezone'].initial = 'UTC'

    def clean_title(self):
        """Validate meeting title."""
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise ValidationError('Meeting title is required.')
        
        if len(title) < 3:
            raise ValidationError('Meeting title must be at least 3 characters long.')
        
        if len(title) > 200:
            raise ValidationError('Meeting title must not exceed 200 characters.')
        
        return title

    def clean_scheduled_at(self):
        """Validate that meeting date is not in the past."""
        scheduled_at = self.cleaned_data.get('scheduled_at')
        
        if not scheduled_at:
            raise ValidationError('Scheduled date and time is required.')
        
        now = timezone.now()
        # Allow 1 minute grace period for timezone differences
        if scheduled_at < (now - timezone.timedelta(minutes=1)):
            raise ValidationError(
                'Meeting cannot be scheduled in the past. '
                'Please select a date and time in the future.'
            )
        
        return scheduled_at

    def clean_duration_minutes(self):
        """Validate duration is within acceptable range."""
        duration = self.cleaned_data.get('duration_minutes')
        
        if not duration:
            raise ValidationError('Duration is required.')
        
        if duration < 15:
            raise ValidationError('Meeting duration must be at least 15 minutes.')
        
        if duration > 480:
            raise ValidationError('Meeting duration cannot exceed 8 hours (480 minutes).')
        
        return duration

    def clean_meeting_link(self):
        """Validate meeting link format for remote platforms."""
        platform = self.cleaned_data.get('platform')
        meeting_link = (self.cleaned_data.get('meeting_link') or '').strip()
        
        remote_platforms = ['zoom', 'teams', 'slack', 'google_meet']
        
        # Check if link is required for remote platforms
        if platform in remote_platforms and not meeting_link:
            raise ValidationError(
                f'Meeting link is required for {platform.title()} meetings. '
                'Please provide the URL for joining the meeting.'
            )
        
        # Validate link format if provided
        if meeting_link:
            try:
                result = urlparse(meeting_link)
                if not all([result.scheme, result.netloc]):
                    raise ValidationError(
                        'Invalid meeting link format. '
                        'Please provide a complete URL (e.g., https://zoom.us/j/...)'
                    )
            except Exception:
                raise ValidationError('Invalid meeting link format.')
        
        return meeting_link

    def clean(self):
        """Validate form data across multiple fields."""
        cleaned_data = super().clean()
        team = cleaned_data.get('team')
        attendees = cleaned_data.get('attendees')
        
        # Validate attendees for team meetings
        if team and not attendees:
            self.add_error(
                'attendees',
                'Team meetings must have at least one attendee invited.'
            )
        
        return cleaned_data

    def save(self, commit=True, user=None):
        """Save meeting and add attendees."""
        meeting = super().save(commit=commit)
        
        # Add attendees to the meeting
        if commit:
            attendees = self.cleaned_data.get('attendees', [])
            # Clear existing attendees and add new ones
            MeetingAttendee.objects.filter(meeting=meeting).delete()
            for attendee in attendees:
                MeetingAttendee.objects.create(
                    meeting=meeting,
                    user=attendee,
                    rsvp_status='pending'
                )
        
        return meeting


class MeetingAttendeeForm(forms.ModelForm):
    """Form for managing meeting attendee RSVP responses."""

    class Meta:
        model = MeetingAttendee
        fields = ['rsvp_status']
        widgets = {
            'rsvp_status': forms.Select(attrs={
                'class': 'px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-gray-700 dark:text-white dark:border-gray-600',
            }),
        }

    def clean_rsvp_status(self):
        """Validate RSVP status."""
        status = self.cleaned_data.get('rsvp_status')
        
        if not status:
            raise ValidationError('Please select an RSVP status.')
        
        valid_statuses = ['accepted', 'declined', 'tentative', 'pending']
        if status not in valid_statuses:
            raise ValidationError('Invalid RSVP status selected.')
        
        return status

