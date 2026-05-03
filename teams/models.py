from django.db import models
from django.contrib.auth.models import User
from department.models import Department

# Create your models here.

class TeamType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team_types'


class Team(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('restructured', 'Restructured'),
        ('disbanded', 'Disbanded'),
    ]

    # Identity
    name = models.CharField(max_length=150, unique=True)

    # Relationships
    department = models.ForeignKey(
        Department,
        on_delete=models.RESTRICT,
        related_name='teams'
    )

    team_type = models.ForeignKey(
        TeamType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams'
    )

    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_teams'
    )

    # Purpose & description
    mission = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Agile / project management
    jira_project_name = models.CharField(max_length=150, blank=True, null=True)
    jira_board_link = models.URLField(blank=True, null=True)
    workstream = models.CharField(max_length=150, blank=True, null=True)
    agile_practices = models.TextField(blank=True, null=True)
    concurrent_projects = models.CharField(max_length=20, blank=True, null=True)

    # Engineering metadata
    development_focus = models.TextField(blank=True, null=True)
    key_skills = models.TextField(blank=True, null=True)
    versioning_approach = models.TextField(blank=True, null=True)

    # Communication
    slack_channels = models.TextField(blank=True, null=True)
    daily_standup_link = models.URLField(blank=True, null=True)
    team_wiki_url = models.URLField(blank=True, null=True)
    wiki_search_terms = models.TextField(blank=True, null=True)

    # Lifecycle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    disbanded_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team'
        ordering = ['name']

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        related_name='members'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )

    role = models.CharField(max_length=100, blank=True, null=True)

    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'team_member'
        unique_together = ('team', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"