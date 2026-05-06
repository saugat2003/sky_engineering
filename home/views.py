from datetime import timedelta

from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.models import UserProfile
from department.models import Department
from messaging.models import Message
from scheduling.models import Meeting
from teams.models import AuditTrail, Team, TeamDependency, TeamMember
from scheduling.models import Notification


@login_required
def home_redirect(request):
    now = timezone.now()
    horizon = now + timedelta(days=7)

    departments = Department.objects.annotate(
        total_teams=Count('teams', distinct=True),
        active_teams=Count('teams', filter=Q(teams__status='active'), distinct=True),
        total_members=Count('teams__members__user', filter=Q(teams__members__is_active=True), distinct=True),
    ).order_by('name')

    max_department_teams = max([department.total_teams for department in departments], default=0) or 1
    department_cards = [
        {
            'department': department,
            'team_width': round((department.total_teams / max_department_teams) * 100),
        }
        for department in departments[:4]
    ]

    context = {
        'total_departments': Department.objects.count(),
        'active_departments': Department.objects.filter(is_active=True).count(),
        'total_teams': Team.objects.count(),
        'active_teams': Team.objects.filter(status='active').count(),
        'total_engineers': TeamMember.objects.filter(is_active=True).values('user_id').distinct().count(),
        'total_dependencies': TeamDependency.objects.count(),
        'upcoming_meetings': (
            Meeting.objects.filter(scheduled_at__gte=now, scheduled_at__lte=horizon, status='scheduled')
            .select_related('team', 'organiser')
            .prefetch_related('attendees')
            .order_by('scheduled_at')[:5]
        ),
        'recent_messages': (
            Message.objects.filter(recipient=request.user, status=Message.Status.INBOX)
            .select_related('sender')
            .order_by('-created_at')[:5]
        ),
        'recent_audits': (
            AuditTrail.objects.select_related('team', 'team__department', 'edited_by')
            .order_by('-timestamp')[:5]
        ),
        'recent_teams': (
            Team.objects.select_related('department', 'manager', 'team_type')
            .annotate(member_count=Count('members', filter=Q(members__is_active=True), distinct=True))
            .order_by('-updated_at')[:4]
        ),
        'department_cards': department_cards,
        'draft_count': Message.objects.filter(sender=request.user, status=Message.Status.DRAFT).count(),
    }
    return render(request, 'home/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user_id=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.save()

            profile.phone = request.POST.get('phone', '').strip()
            profile.bio = request.POST.get('bio', '').strip()
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()

            messages.success(request, 'Profile updated successfully.')

        elif form_type == 'password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password updated successfully.')
            else:
                for field_errors in password_form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)
            return redirect('profile')

        return redirect('profile')

    context = {
        'profile': profile,
        'password_form': PasswordChangeForm(user),
    }
    return render(request, 'home/profile.html', context)


@require_POST
@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})
