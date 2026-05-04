"""Views for meeting scheduling and calendar management."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.db import transaction
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from calendar import monthcalendar, month_name
import json

from .models import Meeting, MeetingAttendee
from .forms import MeetingForm, MeetingAttendeeForm
from .utils import notify_meeting_created, notify_meeting_updated, notify_meeting_cancelled


@login_required
def schedule_meeting(request):
    """Handle meeting creation and editing."""
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organiser = request.user
            meeting.save()

            attendees = form.cleaned_data.get('attendees', [])
            attendee_users = list(attendees)
            for attendee in attendee_users:
                MeetingAttendee.objects.create(meeting=meeting, user=attendee)

            transaction.on_commit(lambda: notify_meeting_created(meeting))

            return redirect('scheduling:meeting_detail', pk=meeting.id)
    else:
        form = MeetingForm()
    
    context = {
        'form': form,
        'title': 'Schedule Meeting',
    }
    return render(request, 'scheduling/schedule_meeting.html', context)


@login_required
def monthly_calendar(request):
    """Display meetings in a monthly calendar grid."""
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Get all meetings for the requested month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    meetings = Meeting.objects.filter(
        scheduled_at__date__range=[start_date, end_date],
        status='scheduled'
    ).select_related('organiser', 'team')
    
    # Build calendar grid
    cal = monthcalendar(year, month)
    weeks = []
    for week in cal:
        week_data = []
        for day in week:
            day_meetings = []
            if day != 0:
                day_date = date(year, month, day)
                day_meetings = [m for m in meetings if m.scheduled_at.date() == day_date]
            
            week_data.append({
                'day': day,
                'meetings': day_meetings,
                'date': date(year, month, day) if day != 0 else None,
            })
        weeks.append(week_data)
    
    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1
    
    context = {
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'weeks': weeks,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today': datetime.now().date(),
        'day_names': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    }
    
    return render(request, 'scheduling/monthly_calendar.html', context)


@login_required
def weekly_calendar(request):
    """Display meetings in a weekly view."""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    requested_week = request.GET.get('week')
    if requested_week:
        week_start = datetime.strptime(requested_week, '%Y-%m-%d').date()
        if week_start.weekday() != 0:
            week_start = week_start - timedelta(days=week_start.weekday())
        week_end = week_start + timedelta(days=6)
    
    # Get meetings for the week
    meetings = Meeting.objects.filter(
        scheduled_at__date__range=[week_start, week_end],
        status='scheduled'
    ).select_related('organiser', 'team').order_by('scheduled_at')
    
    # Build week grid with hourly slots
    days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_meetings = [m for m in meetings if m.scheduled_at.date() == day_date]
        days.append({
            'date': day_date,
            'day_name': day_date.strftime('%A'),
            'meetings': day_meetings,
            'is_today': day_date == today,
        })
    
    # Navigation
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    
    context = {
        'week_start': week_start,
        'week_end': week_end,
        'days': days,
        'prev_week': prev_week,
        'next_week': next_week,
        'today': today,
    }
    
    return render(request, 'scheduling/weekly_calendar.html', context)


@login_required
def upcoming_schedules(request):
    """Display upcoming meetings sorted by date."""
    today = datetime.now()
    
    # Filter parameters
    platform = request.GET.get('platform')
    team_id = request.GET.get('team')
    days_ahead = int(request.GET.get('days', 30))
    
    # Get upcoming meetings
    meetings_qs = Meeting.objects.filter(
        scheduled_at__gte=today,
        status='scheduled'
    ).select_related('organiser', 'team').order_by('scheduled_at')
    
    # Apply filters
    if platform:
        meetings_qs = meetings_qs.filter(platform=platform)
    if team_id:
        meetings_qs = meetings_qs.filter(team_id=team_id)
    
    meetings_qs = meetings_qs.filter(scheduled_at__lte=today + timedelta(days=days_ahead))
    
    # Group by date
    meetings_by_date = {}
    for meeting in meetings_qs:
        meeting_date = meeting.scheduled_at.date()
        if meeting_date not in meetings_by_date:
            meetings_by_date[meeting_date] = []
        meetings_by_date[meeting_date].append(meeting)
    
    # Get all platforms and teams for filter dropdowns
    platforms = Meeting.PLATFORM_CHOICES
    from teams.models import Team
    teams = Team.objects.filter(status='active').order_by('name')
    
    context = {
        'meetings_by_date': sorted(meetings_by_date.items()),
        'total_meetings': sum(len(m) for m in meetings_by_date.values()),
        'platforms': platforms,
        'teams': teams,
        'selected_platform': platform,
        'selected_team': team_id,
        'days_ahead': days_ahead,
    }
    
    return render(request, 'scheduling/upcoming_schedules.html', context)


@login_required
def meeting_detail(request, pk):
    """Display detailed information about a meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Get attendee list
    attendees = meeting.attendees.select_related('user').order_by('rsvp_status')
    
    # Check if user is organiser or attendee
    is_organiser = meeting.organiser == request.user
    is_attendee = attendees.filter(user=request.user).exists()
    
    # Handle RSVP updates
    if request.method == 'POST' and is_attendee:
        rsvp_status = request.POST.get('rsvp_status')
        attendee = attendees.filter(user=request.user).first()
        if attendee:
            attendee.rsvp_status = rsvp_status
            attendee.save()
            return redirect('scheduling:meeting_detail', pk=meeting.id)
    
    context = {
        'meeting': meeting,
        'attendees': attendees,
        'is_organiser': is_organiser,
        'is_attendee': is_attendee,
        'days_until': (meeting.scheduled_at.date() - datetime.now().date()).days,
    }
    
    return render(request, 'scheduling/meeting_detail.html', context)


@login_required
def edit_meeting(request, pk):
    """Edit an existing meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Check permissions
    if meeting.organiser != request.user:
        return redirect('scheduling:meeting_detail', pk=pk)
    
    if request.method == 'POST':
        previous_attendees = list(meeting.attendees.select_related('user').all())
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            
            # Update attendees
            current_attendees = set(
                meeting.attendees.values_list('user_id', flat=True)
            )
            new_attendees = set(
                int(aid) for aid in request.POST.getlist('attendees')
            )

            added_attendees = []
            removed_attendees = []
            
            # Add new attendees
            for attendee_id in new_attendees - current_attendees:
                from django.contrib.auth.models import User
                attendee_user = User.objects.filter(pk=attendee_id).first()
                MeetingAttendee.objects.create(meeting=meeting, user_id=attendee_id)
                if attendee_user:
                    added_attendees.append(attendee_user)
            
            # Remove attendees
            for attendee_id in current_attendees - new_attendees:
                attendee_user = next((item.user for item in previous_attendees if item.user_id == attendee_id), None)
                meeting.attendees.filter(user_id=attendee_id).delete()
                if attendee_user:
                    removed_attendees.append(attendee_user)

            transaction.on_commit(
                lambda: notify_meeting_updated(
                    meeting,
                    added_users=added_attendees,
                    removed_users=removed_attendees,
                )
            )
            
            return redirect('scheduling:meeting_detail', pk=meeting.id)
    else:
        form = MeetingForm(instance=meeting)
    
    current_attendees = list(
        meeting.attendees.values_list('user_id', flat=True)
    )
    
    context = {
        'form': form,
        'meeting': meeting,
        'title': f'Edit Meeting: {meeting.title}',
        'current_attendees': current_attendees,
    }
    
    return render(request, 'scheduling/schedule_meeting.html', context)


@login_required
def cancel_meeting(request, pk):
    """Cancel a meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    if meeting.organiser != request.user:
        return redirect('scheduling:meeting_detail', pk=pk)
    
    if request.method == 'POST':
        meeting.status = 'cancelled'
        meeting.save()
        transaction.on_commit(lambda: notify_meeting_cancelled(meeting))
        return redirect('scheduling:upcoming_schedules')
    
    context = {'meeting': meeting}
    return render(request, 'scheduling/cancel_meeting.html', context)
