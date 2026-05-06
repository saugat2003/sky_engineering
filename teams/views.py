from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from department.models import Department
from teams.forms import TeamEmailForm, TeamForm
from teams.models import AuditTrail, Skill, Team, TeamDependency, TeamEmail, TeamType


def _team_queryset():
    return (
        Team.objects.select_related('department', 'team_type', 'manager')
        .prefetch_related(
            'members__user',
            'repositories',
            'software_products',
            'contact_channels',
            'skills',
            'downstream_dependencies__to_team',
            'upstream_dependencies__from_team',
            'audit_trails__edited_by',
        )
        .annotate(member_count=Count('members', filter=Q(members__is_active=True), distinct=True))
        .order_by('name')
    )


def _filtered_teams(request):
    teams = _team_queryset()
    query = request.GET.get('q', '').strip()
    department_id = request.GET.get('department', '').strip()
    manager_id = request.GET.get('manager', '').strip()
    team_type_id = request.GET.get('team_type', '').strip()
    status = request.GET.get('status', '').strip()

    if query:
        teams = teams.filter(
            Q(name__icontains=query)
            | Q(department__name__icontains=query)
            | Q(manager__first_name__icontains=query)
            | Q(manager__last_name__icontains=query)
            | Q(manager__username__icontains=query)
            | Q(mission__icontains=query)
            | Q(description__icontains=query)
        )
    if department_id:
        teams = teams.filter(department_id=department_id)
    if manager_id:
        teams = teams.filter(manager_id=manager_id)
    if team_type_id:
        teams = teams.filter(team_type_id=team_type_id)
    if status:
        teams = teams.filter(status=status)

    return teams


def _filter_context(request):
    managers = (
        Team.objects.filter(manager__isnull=False)
        .select_related('manager')
        .values('manager_id', 'manager__first_name', 'manager__last_name', 'manager__username')
        .distinct()
        .order_by('manager__first_name', 'manager__username')
    )
    return {
        'departments': Department.objects.all(),
        'team_types': TeamType.objects.all(),
        'managers': managers,
        'status_choices': Team.STATUS_CHOICES,
        'selected_query': request.GET.get('q', ''),
        'selected_department': request.GET.get('department', ''),
        'selected_manager': request.GET.get('manager', ''),
        'selected_team_type': request.GET.get('team_type', ''),
        'selected_status': request.GET.get('status', ''),
    }


@login_required
def team_list(request):
    teams = _filtered_teams(request)
    paginator = Paginator(teams, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        **_filter_context(request),
        'page_obj': page_obj,
        'teams': page_obj.object_list,
        'total_teams': teams.count(),
        'total_dependencies': TeamDependency.objects.count(),
        'view_mode': request.GET.get('view', 'grid'),
    }
    return render(request, 'teams/team_list.html', context)


@login_required
def team_search(request):
    teams = _filtered_teams(request)
    paginator = Paginator(teams, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        **_filter_context(request),
        'page_obj': page_obj,
        'teams': page_obj.object_list,
        'total_teams': teams.count(),
    }
    return render(request, 'teams/team_search.html', context)


@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.is_active = team.status == 'active'
            team.save()
            form.save_m2m()
            AuditTrail.objects.create(
                team=team,
                edited_by=request.user,
                edit_description='Team created from the registry UI.',
            )
            messages.success(request, f'{team.name} was added to the team registry.')
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm()

    context = {
        'form': form,
        'total_departments': Department.objects.count(),
        'total_team_types': TeamType.objects.count(),
        'total_skills': Skill.objects.count(),
    }
    return render(request, 'teams/team_form.html', context)


@login_required
def team_detail(request, pk):
    team = get_object_or_404(_team_queryset(), pk=pk)
    context = {
        'team': team,
        'upstream_dependencies': team.downstream_dependencies.select_related('to_team', 'to_team__department'),
        'downstream_dependencies': team.upstream_dependencies.select_related('from_team', 'from_team__department'),
        'audit_trails': team.audit_trails.select_related('edited_by')[:8],
    }
    return render(request, 'teams/team_detail.html', context)


@login_required
def team_email(request, pk):
    team = get_object_or_404(Team.objects.prefetch_related('contact_channels'), pk=pk)
    initial = {
        'recipient': team.primary_contact or team.primary_slack,
        'subject': f'Update for {team.name}',
    }
    if request.method == 'POST':
        form = TeamEmailForm(request.POST)
        if form.is_valid():
            team_email = form.save(commit=False)
            team_email.team = team
            team_email.sender = request.user
            try:
                if '@' in team_email.recipient:
                    send_mail(
                        team_email.subject,
                        team_email.message,
                        request.user.email or None,
                        [team_email.recipient],
                        fail_silently=False,
                    )
                team_email.delivered = True
                team_email.save()
                AuditTrail.objects.create(
                    team=team,
                    edited_by=request.user,
                    edit_description=f'Email sent to {team_email.recipient}: {team_email.subject}',
                )
                messages.success(request, 'Team email was sent and stored successfully.')
                return redirect('team_detail', pk=team.pk)
            except Exception as exc:
                team_email.delivered = False
                team_email.save()
                messages.error(request, f'Email could not be sent, but the message was stored. {exc}')
    else:
        form = TeamEmailForm(initial=initial)

    return render(request, 'teams/team_email.html', {'team': team, 'form': form})


@login_required
def team_dependencies(request, pk):
    team = get_object_or_404(_team_queryset(), pk=pk)
    context = {
        'team': team,
        'upstream_dependencies': team.downstream_dependencies.select_related('to_team', 'to_team__department'),
        'downstream_dependencies': team.upstream_dependencies.select_related('from_team', 'from_team__department'),
    }
    return render(request, 'teams/team_dependencies.html', context)


@login_required
def team_skills(request, pk):
    team = get_object_or_404(_team_queryset(), pk=pk)
    return render(request, 'teams/team_skills.html', {'team': team, 'all_skills': Skill.objects.all()})


@login_required
def schedule_team_meeting(request, pk):
    team = get_object_or_404(Team, pk=pk)
    url = f"{reverse('scheduling:schedule_meeting_create')}?team={team.pk}&title={team.name}"
    return redirect(url)
