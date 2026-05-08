# Authorship: Teams module tests led by Saugat Bhattarai (0xsaugat).
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from department.models import Department
from teams.models import AuditTrail, ContactChannel, Skill, Team, TeamDependency, TeamEmail, TeamMember, TeamType


class TeamViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='manager', password='pass', email='manager@example.com')
        self.client.force_login(self.user)
        self.department = Department.objects.create(name='xTV Web', description='Web platform')
        self.team_type = TeamType.objects.create(name='Platform')
        self.team = Team.objects.create(
            name='Code Warriors',
            department=self.department,
            team_type=self.team_type,
            manager=self.user,
            mission='Owns playback web services.',
            email_address='code.warriors@example.com',
            slack_channel='#code-warriors',
        )
        ContactChannel.objects.create(team=self.team, channel_type='email', value='code.warriors@example.com', is_primary=True)
        Skill.objects.create(name='Django', description='Backend web framework')
        Skill.objects.create(name='Incident Management', description='Incident response and comms')
        self.team.skills.add(Skill.objects.get(name='Django'))
        for index in range(5):
            member = User.objects.create_user(username=f'engineer{index}', password='pass')
            TeamMember.objects.create(team=self.team, user=member, role='Software Engineer')

    def test_team_pages_render_for_logged_in_user(self):
        urls = [
            reverse('team_list'),
            reverse('team_create'),
            reverse('team_search'),
            reverse('team_detail', args=[self.team.pk]),
            reverse('team_email', args=[self.team.pk]),
            reverse('team_dependencies', args=[self.team.pk]),
            reverse('team_skills', args=[self.team.pk]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_search_finds_team_by_department_and_manager(self):
        response = self.client.get(reverse('team_search'), {'q': 'manager'})

        self.assertContains(response, 'Code Warriors')
        self.assertContains(response, 'xTV Web')

    def test_email_form_stores_team_message(self):
        response = self.client.post(
            reverse('team_email', args=[self.team.pk]),
            {
                'recipient': 'code.warriors@example.com',
                'subject': 'Release update',
                'message': 'Please review the deployment notes.',
            },
        )

        self.assertRedirects(response, reverse('team_detail', args=[self.team.pk]))
        self.assertTrue(TeamEmail.objects.filter(team=self.team, subject='Release update').exists())

    def test_create_team_form_adds_registry_record(self):
        response = self.client.post(
            reverse('team_create'),
            {
                'name': 'Signal Reliability',
                'department': self.department.pk,
                'team_type': self.team_type.pk,
                'manager': self.user.pk,
                'status': 'active',
                'mission': 'Owns signal monitoring and alerting.',
                'description': 'Keeps broadcast reliability visible.',
                'workstream': 'Broadcast Operations',
                'development_focus': 'Observability and incident response.',
                'key_skills': 'Django, monitoring',
                'email_address': 'signal@example.com',
                'slack_channel': '#signal-reliability',
                'daily_standup_link': '',
                'team_wiki_url': '',
                'jira_project_name': 'SIG',
                'jira_board_link': '',
                'skills': [Skill.objects.get(name='Django').pk],
            },
        )

        team = Team.objects.get(name='Signal Reliability')
        self.assertRedirects(response, reverse('team_detail', args=[team.pk]))
        self.assertTrue(team.skills.filter(name='Django').exists())
        self.assertTrue(AuditTrail.objects.filter(team=team, edit_description__icontains='created').exists())

    def test_schedule_button_redirects_with_team_prefill(self):
        response = self.client.get(reverse('team_schedule', args=[self.team.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/scheduling/create/', response['Location'])
        self.assertIn(f'team={self.team.pk}', response['Location'])

    def test_dependency_page_adds_and_removes_upstream_dependency(self):
        target = Team.objects.create(
            name='Playback API',
            department=self.department,
            team_type=self.team_type,
            manager=self.user,
            mission='Provides playback APIs.',
        )

        add_response = self.client.post(
            reverse('team_dependencies', args=[self.team.pk]),
            {
                'action': 'add',
                'to_team': target.pk,
                'dependency_type': 'API',
                'description': 'Consumes playback API availability data.',
            },
        )

        self.assertRedirects(add_response, reverse('team_dependencies', args=[self.team.pk]))
        dependency = TeamDependency.objects.get(from_team=self.team, to_team=target)
        self.assertEqual(dependency.dependency_type, 'API')
        self.assertTrue(AuditTrail.objects.filter(team=self.team, edit_description__icontains='Dependency added').exists())

        remove_response = self.client.post(
            reverse('team_dependencies', args=[self.team.pk]),
            {'action': 'remove', 'dependency_id': dependency.pk},
        )

        self.assertRedirects(remove_response, reverse('team_dependencies', args=[self.team.pk]))
        self.assertFalse(TeamDependency.objects.filter(pk=dependency.pk).exists())
        self.assertTrue(AuditTrail.objects.filter(team=self.team, edit_description__icontains='Dependency removed').exists())

    def test_skill_page_adds_and_removes_team_skill(self):
        skill = Skill.objects.get(name='Incident Management')

        add_response = self.client.post(
            reverse('team_skills', args=[self.team.pk]),
            {'action': 'add', 'skill': skill.pk},
        )

        self.assertRedirects(add_response, reverse('team_skills', args=[self.team.pk]))
        self.assertTrue(self.team.skills.filter(pk=skill.pk).exists())
        self.assertTrue(AuditTrail.objects.filter(team=self.team, edit_description__icontains='Skill added').exists())

        remove_response = self.client.post(
            reverse('team_skills', args=[self.team.pk]),
            {'action': 'remove', 'skill_id': skill.pk},
        )

        self.assertRedirects(remove_response, reverse('team_skills', args=[self.team.pk]))
        self.assertFalse(self.team.skills.filter(pk=skill.pk).exists())
        self.assertTrue(AuditTrail.objects.filter(team=self.team, edit_description__icontains='Skill removed').exists())
