from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.models import UserProfile
from department.models import Department
from teams.models import Team, TeamMember, AuditTrail
from scheduling.models import Notification


@login_required
def home_redirect(request):
    dept_count = Department.objects.count()
    team_count = Team.objects.count()
    engineer_count = TeamMember.objects.count()
    departments = Department.objects.prefetch_related('teams').order_by('name')[:4]
    recent_changes = AuditTrail.objects.select_related(
        'team', 'team__department', 'edited_by'
    ).order_by('-timestamp')[:5]
    return render(request, 'home/dashboard.html', {
        'dept_count': dept_count,
        'team_count': team_count,
        'engineer_count': engineer_count,
        'departments': departments,
        'recent_changes': recent_changes,
    })


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
