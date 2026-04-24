"""Models for meeting scheduling and calendar management."""

from django.db import models
from django.contrib.auth.models import User
from teams.models import Team
from datetime import datetime, timedelta


class Meeting(models.Model):
    """Represents a scheduled meeting with attendees and platform info."""

    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('slack', 'Slack'),
        ('google_meet', 'Google Meet'),
        ('in_person', 'In-Person'),
        ('hybrid', 'Hybrid'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
    ]

    # Core meeting details
    title = models.CharField(max_length=255, help_text='Meeting title or subject')
    description = models.TextField(blank=True, null=True, help_text='Agenda or meeting details')
    organiser = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organised_meetings',
        help_text='User who created the meeting'
    )

    # Scheduling
    scheduled_at = models.DateTimeField(help_text='When the meeting is scheduled')
    duration_minutes = models.IntegerField(default=60, help_text='Meeting duration in minutes')
    timezone = models.CharField(max_length=50, default='UTC', help_text='Timezone for the meeting')

    # Meeting location/platform
    platform = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        default='zoom',
        help_text='Meeting platform (Zoom, Teams, etc.)'
    )
    meeting_link = models.URLField(blank=True, null=True, help_text='Video call or meeting link')

    # Team association
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings',
        help_text='Associated team (optional)'
    )

    # Meeting lifecycle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text='Current status of the meeting'
    )
    recurrence = models.CharField(
        max_length=20,
        choices=RECURRENCE_CHOICES,
        default='none',
        help_text='Recurrence pattern'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meeting'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['organiser', 'scheduled_at']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['team', 'scheduled_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.scheduled_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def end_time(self):
        """Calculate the meeting end time."""
        return self.scheduled_at + timedelta(minutes=self.duration_minutes)

    @property
    def is_upcoming(self):
        """Check if meeting is in the future."""
        return self.scheduled_at > datetime.now() and self.status == 'scheduled'

    @property
    def is_today(self):
        """Check if meeting is today."""
        today = datetime.now().date()
        return self.scheduled_at.date() == today

    @property
    def attendee_count(self):
        """Return the number of attendees including organiser."""
        return self.attendees.count() + 1

    @property
    def accepted_count(self):
        """Return the number of accepted RSVPs."""
        return self.attendees.filter(rsvp_status='accepted').count() + 1


class MeetingAttendee(models.Model):
    """Tracks attendees and their RSVP status for a meeting."""

    RSVP_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('tentative', 'Tentative'),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attendees',
        help_text='The meeting this attendee is registered for'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meeting_attendances',
        help_text='User attending the meeting'
    )
    rsvp_status = models.CharField(
        max_length=20,
        choices=RSVP_CHOICES,
        default='pending',
        help_text='RSVP status for this attendee'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meeting_attendee'
        unique_together = ('meeting', 'user')
        ordering = ['rsvp_status', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.meeting.title} ({self.rsvp_status})"
