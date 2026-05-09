"""Tests for the home app.
Author: Saugat Bhattarai and Rupesh Dahal
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from department.models import Department
from messaging.models import Message
from scheduling.models import Meeting
from teams.models import AuditTrail, Team, TeamDependency, TeamMember, TeamType


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager',
            password='pass',
            email='manager@example.com',
            first_name='Mina',
            last_name='Manager',
        )
        self.sender = User.objects.create_user(username='sender', password='pass', email='sender@example.com')
        self.engineer = User.objects.create_user(username='engineer', password='pass')
        self.client.force_login(self.user)

        self.department = Department.objects.create(name='Backend Teams', description='Backend platform work')
        self.team_type = TeamType.objects.create(name='Backend')
        self.team = Team.objects.create(
            name='API Platform',
            department=self.department,
            team_type=self.team_type,
            manager=self.user,
            mission='Builds backend APIs.',
            email_address='api@example.com',
            status='active',
        )
        self.consumer_team = Team.objects.create(
            name='Web Experience',
            department=self.department,
            team_type=self.team_type,
            mission='Consumes API capabilities.',
            status='active',
        )
        TeamMember.objects.create(team=self.team, user=self.engineer, role='Software Engineer')
        TeamDependency.objects.create(from_team=self.consumer_team, to_team=self.team, dependency_type='API')
        AuditTrail.objects.create(team=self.team, edited_by=self.user, edit_description='Team created from tests.')
        Message.objects.create(
            sender=self.sender,
            recipient=self.user,
            subject='Release readiness',
            body='Please review the backend release plan.',
            status=Message.Status.INBOX,
            is_read=False,
            sent_at=timezone.now(),
        )
        Meeting.objects.create(
            title='API planning',
            organiser=self.user,
            scheduled_at=timezone.now() + timedelta(days=1),
            duration_minutes=30,
            platform='teams',
            team=self.team,
            status='scheduled',
        )

    def test_dashboard_renders_dynamic_operational_summary(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Engineering Command Center')
        self.assertContains(response, 'Backend Teams')
        self.assertContains(response, 'API Platform')
        self.assertContains(response, 'API planning')
        self.assertContains(response, 'Release readiness')
        self.assertContains(response, '1 unread message')
        self.assertContains(response, 'Registry Activity')
        self.assertNotContains(response, 'Teams without manager')
        self.assertNotContains(response, 'Meetings today')

    def test_dashboard_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response['Location'])
