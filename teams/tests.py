from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from department.models import Department
from teams.models import ContactChannel, Skill, Team, TeamEmail, TeamMember, TeamType


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
        self.team.skills.add(Skill.objects.get(name='Django'))
        for index in range(5):
            member = User.objects.create_user(username=f'engineer{index}', password='pass')
            TeamMember.objects.create(team=self.team, user=member, role='Software Engineer')

    def test_team_pages_render_for_logged_in_user(self):
        urls = [
            reverse('team_list'),
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

    def test_schedule_button_redirects_with_team_prefill(self):
        response = self.client.get(reverse('team_schedule', args=[self.team.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/scheduling/create/', response['Location'])
        self.assertIn(f'team={self.team.pk}', response['Location'])
