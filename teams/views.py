from django.shortcuts import render
from teams.models import Team, TeamDependency, TeamType

def team_list(request):
    teams = Team.objects.select_related(
        'department',
        'team_type',
        'manager',
    ).prefetch_related(
        'members',
        'downstream_dependencies__to_team',
        'upstream_dependencies__from_team',
    )

    context = {
        'teams': teams,
        'team_types': TeamType.objects.all(),
        'dependencies': TeamDependency.objects.select_related('from_team', 'to_team'),
    }
    return render(request, 'teams/team_list.html', context)
