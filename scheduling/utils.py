"""Utility helpers for meeting notifications."""

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone


def format_meeting_datetime(meeting):
    """Return a human-readable meeting date range."""
    scheduled_at = timezone.localtime(meeting.scheduled_at)
    end_time = timezone.localtime(meeting.end_time)
    return (
        scheduled_at.strftime("%A, %B %d, %Y at %H:%M"),
        end_time.strftime("%H:%M"),
    )


def build_meeting_email_subject(action, meeting):
    """Build a concise email subject for a meeting notification."""
    return f"[Scheduling] Meeting {action}: {meeting.title}"


def build_meeting_email_body(action, meeting, recipient_name=None):
    """Build the plain-text notification body."""
    meeting_start, meeting_end = format_meeting_datetime(meeting)
    organizer_name = meeting.organiser.get_full_name() or meeting.organiser.username
    team_name = meeting.team.name if meeting.team else "No team assigned"
    greeting = f"Hello {recipient_name},\n\n" if recipient_name else ""

    return (
        f"{greeting}"
        f"The meeting below has been {action}.\n\n"
        f"Title: {meeting.title}\n"
        f"When: {meeting_start} - {meeting_end} ({meeting.timezone})\n"
        f"Platform: {meeting.get_platform_display()}\n"
        f"Team: {team_name}\n"
        f"Organizer: {organizer_name}\n"
        f"Status: {meeting.get_status_display()}\n"
        f"Duration: {meeting.duration_minutes} minutes\n"
    )


def send_meeting_notification(meeting, recipients, action, recipient_name=None):
    """Send a meeting notification email to a list of recipients."""
    emails = [email for email in recipients if email]
    if not emails:
        return 0

    send_mail(
        subject=build_meeting_email_subject(action, meeting),
        message=build_meeting_email_body(action, meeting, recipient_name=recipient_name),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=emails,
        fail_silently=True,
    )
    return len(emails)


def _create_in_app_notification(user, message, meeting):
    """Create an in-app Notification record for the given user."""
    from scheduling.models import Notification
    try:
        link = reverse('scheduling:meeting_detail', args=[meeting.pk])
    except Exception:
        link = None
    Notification.objects.create(user=user, message=message, link=link)


def notify_meeting_created(meeting):
    """Notify organizer and attendees that a meeting was created."""
    organizer_name = meeting.organiser.get_full_name() or meeting.organiser.username
    send_meeting_notification(meeting, [meeting.organiser.email], "created", recipient_name=organizer_name)
    _create_in_app_notification(meeting.organiser, f'Meeting created: "{meeting.title}"', meeting)

    for attendee in meeting.attendees.select_related("user").all():
        attendee_name = attendee.user.get_full_name() or attendee.user.username
        send_meeting_notification(meeting, [attendee.user.email], "scheduled", recipient_name=attendee_name)
        _create_in_app_notification(attendee.user, f'You have been invited to: "{meeting.title}"', meeting)


def notify_meeting_updated(meeting, added_users=None, removed_users=None):
    """Notify participants that a meeting was updated."""
    recipient_map = {}

    organizer_name = meeting.organiser.get_full_name() or meeting.organiser.username
    if meeting.organiser.email:
        recipient_map[meeting.organiser.email] = organizer_name

    for attendee in meeting.attendees.select_related("user").all():
        if attendee.user.email:
            recipient_map[attendee.user.email] = attendee.user.get_full_name() or attendee.user.username

    for user in added_users or []:
        if user.email:
            recipient_map[user.email] = user.get_full_name() or user.username

    for user in removed_users or []:
        if user.email:
            recipient_map[user.email] = user.get_full_name() or user.username

    all_users = set()
    for email, recipient_name in recipient_map.items():
        send_meeting_notification(meeting, [email], "updated", recipient_name=recipient_name)

    for attendee in meeting.attendees.select_related("user").all():
        _create_in_app_notification(attendee.user, f'Meeting updated: "{meeting.title}"', meeting)
        all_users.add(attendee.user.pk)
    if meeting.organiser.pk not in all_users:
        _create_in_app_notification(meeting.organiser, f'Meeting updated: "{meeting.title}"', meeting)


def notify_meeting_cancelled(meeting):
    """Notify organizer and attendees that a meeting was cancelled."""
    if meeting.organiser.email:
        organizer_name = meeting.organiser.get_full_name() or meeting.organiser.username
        send_meeting_notification(meeting, [meeting.organiser.email], "cancelled", recipient_name=organizer_name)
    _create_in_app_notification(meeting.organiser, f'Meeting cancelled: "{meeting.title}"', meeting)

    for attendee in meeting.attendees.select_related("user").all():
        if attendee.user.email:
            attendee_name = attendee.user.get_full_name() or attendee.user.username
            send_meeting_notification(meeting, [attendee.user.email], "cancelled", recipient_name=attendee_name)
        _create_in_app_notification(attendee.user, f'Meeting cancelled: "{meeting.title}"', meeting)