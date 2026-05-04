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
    email_address = models.EmailField(blank=True, null=True)
    slack_channel = models.CharField(max_length=120, blank=True, null=True)
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
    is_active = models.BooleanField(default=True)
    skills = models.ManyToManyField('Skill', related_name='teams', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def primary_contact(self):
        if self.email_address:
            return self.email_address
        channel = self.contact_channels.filter(channel_type='email').order_by('-is_primary').first()
        return channel.value if channel else ''

    @property
    def primary_slack(self):
        if self.slack_channel:
            return self.slack_channel
        channel = self.contact_channels.filter(channel_type__in=['slack', 'teams']).order_by('-is_primary').first()
        return channel.value if channel else ''


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'skills'
        ordering = ['name']

    def __str__(self):
        return self.name


class TeamDependency(models.Model):
    from_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='downstream_dependencies'
    )

    to_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='upstream_dependencies'
    )

    dependency_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'team_dependency'
        unique_together = ('from_team', 'to_team')
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(from_team=models.F('to_team')),
                name='team_dependency_no_self_reference',
            )
        ]
        ordering = ['from_team__name', 'to_team__name']

    def __str__(self):
        return f"{self.from_team.name} depends on {self.to_team.name}"

class TeamMember(models.Model):
    class RoleChoices(models.TextChoices):
        ENGINEER = 'Software Engineer', 'Software Engineer'
        SENIOR_ENGINEER = 'Senior Engineer', 'Senior Engineer'
        LEAD = 'Team Lead', 'Team Lead'
        PM = 'Product Manager', 'Product Manager'
        AGILE_COACH = 'Agile Coach', 'Agile Coach'
        QA = 'QA Engineer', 'QA Engineer'
        DESIGNER = 'Designer', 'Designer'

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

    role = models.CharField(max_length=100, choices=RoleChoices, default=RoleChoices.ENGINEER)

    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'team_members'
        unique_together = ('team', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"
    

class Repository(models.Model):
    PLATFORM_CHOICES = [
        ('GitHub', 'GitHub'),
        ('GitLab', 'GitLab'),
        ('Bitbucket', 'Bitbucket'),
        ('Other', 'Other'),
    ]

    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        related_name='repositories'
    )

    name = models.CharField(max_length=150)
    url = models.URLField()

    platform = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        default='GitHub'
    )

    description = models.TextField(blank=True, null=True)

    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'repositories'


class SoftwareProduct(models.Model):
    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        related_name='software_products'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'software_products'


class ContactChannel(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('teams', 'Teams'),
        ('other', 'Other'),
    ]

    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        related_name='contact_channels'
    )

    channel_type = models.CharField(
        max_length=50,
        choices=CHANNEL_CHOICES
    )

    value = models.CharField(max_length=255)

    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_channels'


class AuditTrail(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='audit_trails'
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_audit_entries'
    )
    edit_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'team_audit_trails'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.team.name}: {self.edit_description[:60]}"


class TeamEmail(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='emails'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_team_emails'
    )
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=True)

    class Meta:
        db_table = 'team_emails'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.subject} -> {self.recipient}"
