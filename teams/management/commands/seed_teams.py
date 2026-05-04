from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from department.models import Department
from teams.models import (
    AuditTrail,
    ContactChannel,
    Repository,
    Skill,
    Team,
    TeamDependency,
    TeamMember,
    TeamType,
)


class Command(BaseCommand):
    help = 'Seed departments, teams, members, skills, repositories, channels, dependencies, and audit trails.'

    departments = [
        ('xTV Web', 'Customer-facing web video platform and interactive experiences.'),
        ('Broadcast Operations', 'Live signal, media workflow, and operational reliability systems.'),
    ]

    teams = [
        ('Code Warriors', 'xTV Web', 'Product', 'Builds the web playback shell and interactive broadcast features.', ['React', 'TypeScript', 'Django', 'Video.js']),
        ('The Debuggers', 'xTV Web', 'Reliability', 'Troubleshoots player telemetry, quality issues, and release defects.', ['Python', 'Observability', 'Selenium', 'PostgreSQL']),
        ('Bit Masters', 'xTV Web', 'Platform', 'Owns low-latency APIs, encoding metadata, and shared web services.', ['Django', 'Redis', 'GraphQL', 'AWS']),
        ('Signal Core', 'Broadcast Operations', 'Platform', 'Maintains signal ingest, routing, and live event control systems.', ['Go', 'Kafka', 'Linux', 'Networking']),
        ('Cloud Sync', 'Broadcast Operations', 'Infrastructure', 'Synchronizes metadata and event state across cloud regions.', ['AWS', 'Terraform', 'Kubernetes', 'PostgreSQL']),
        ('Media Guardians', 'Broadcast Operations', 'Reliability', 'Protects uptime for broadcast workflows and incident response.', ['SRE', 'Prometheus', 'Grafana', 'Python']),
    ]

    roles = ['Senior Engineer', 'Software Engineer', 'Software Engineer', 'QA Engineer', 'Team Lead']

    def handle(self, *args, **options):
        team_types = {
            name: TeamType.objects.get_or_create(name=name, defaults={'description': f'{name} engineering team'})[0]
            for name in ['Product', 'Platform', 'Reliability', 'Infrastructure']
        }

        departments = {}
        for name, description in self.departments:
            departments[name], _ = Department.objects.get_or_create(
                name=name,
                defaults={'description': description, 'specialisation': description, 'is_active': True},
            )

        skills = {}
        for _, _, _, _, skill_names in self.teams:
            for skill_name in skill_names:
                skills[skill_name], _ = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'description': f'{skill_name} used in delivery and support work.'},
                )

        created_teams = {}
        for index, (team_name, department_name, type_name, mission, skill_names) in enumerate(self.teams, start=1):
            manager = self._user(f'manager{index}', f'Manager {index}', f'{team_name.lower().replace(" ", ".")}.manager@broadcast.local')
            team, _ = Team.objects.update_or_create(
                name=team_name,
                defaults={
                    'department': departments[department_name],
                    'team_type': team_types[type_name],
                    'manager': manager,
                    'mission': mission,
                    'description': mission,
                    'development_focus': 'Delivery ownership, operational support, cross-team dependency management, and predictable release execution.',
                    'email_address': f'{team_name.lower().replace(" ", ".")}@broadcast.local',
                    'slack_channel': f'#{team_name.lower().replace(" ", "-")}',
                    'slack_channels': f'#{team_name.lower().replace(" ", "-")}, #{team_name.lower().replace(" ", "-")}-alerts',
                    'team_wiki_url': f'https://wiki.broadcast.local/teams/{team_name.lower().replace(" ", "-")}',
                    'status': 'active',
                    'is_active': True,
                },
            )
            team.skills.set([skills[name] for name in skill_names])
            created_teams[team_name] = team

            ContactChannel.objects.update_or_create(
                team=team,
                channel_type='email',
                value=team.email_address,
                defaults={'is_primary': True},
            )
            ContactChannel.objects.update_or_create(
                team=team,
                channel_type='slack',
                value=team.slack_channel,
                defaults={'is_primary': True},
            )
            Repository.objects.update_or_create(
                team=team,
                name=f'{team_name} Service',
                defaults={
                    'url': f'https://github.com/broadcast/{team_name.lower().replace(" ", "-")}',
                    'platform': 'GitHub',
                    'description': f'Primary repository for {team_name}.',
                    'is_primary': True,
                },
            )
            AuditTrail.objects.get_or_create(
                team=team,
                edited_by=manager,
                edit_description='Initial seeded team profile created.',
            )

            for member_index, role in enumerate(self.roles, start=1):
                user = self._user(
                    f'{team_name.lower().replace(" ", "_")}_{member_index}',
                    f'{team_name.split()[0]} Engineer {member_index}',
                    f'{team_name.lower().replace(" ", ".")}.{member_index}@broadcast.local',
                )
                TeamMember.objects.update_or_create(
                    team=team,
                    user=user,
                    defaults={'role': role, 'is_active': True},
                )

        self._dependency(created_teams['The Debuggers'], created_teams['Code Warriors'], 'Release validation', 'Debuggers validate player changes before launch.')
        self._dependency(created_teams['Bit Masters'], created_teams['Code Warriors'], 'API contract', 'Bit Masters provides playback metadata APIs.')
        self._dependency(created_teams['Code Warriors'], created_teams['Cloud Sync'], 'Metadata synchronization', 'Web clients depend on synced event state.')
        self._dependency(created_teams['Signal Core'], created_teams['Cloud Sync'], 'Event routing', 'Signal workflows publish cloud event updates.')
        self._dependency(created_teams['Media Guardians'], created_teams['Signal Core'], 'Incident response', 'Reliability work depends on signal health events.')
        self._dependency(created_teams['Cloud Sync'], created_teams['Media Guardians'], 'Operational monitoring', 'Cloud Sync relies on shared SRE telemetry.')

        self.stdout.write(self.style.SUCCESS('Seeded team registry sample data.'))

    def _user(self, username, full_name, email):
        first_name, _, last_name = full_name.partition(' ')
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'is_active': True,
            },
        )
        return user

    def _dependency(self, from_team, to_team, dependency_type, description):
        TeamDependency.objects.update_or_create(
            from_team=from_team,
            to_team=to_team,
            defaults={'dependency_type': dependency_type, 'description': description},
        )
