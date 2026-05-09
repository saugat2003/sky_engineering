# Author: 0xsaugat (Saugat Bhattarai)
from django.contrib import admin

from teams.models import (
    AuditTrail,
    ContactChannel,
    Repository,
    Skill,
    SoftwareProduct,
    Team,
    TeamDependency,
    TeamEmail,
    TeamMember,
    TeamType,
)

# Register your models here.
class TeamMemberInline(admin.TabularInline):
    # Inline editor for team membership records.
    model = TeamMember
    extra = 1


class RepositoryInline(admin.TabularInline):
    # Inline editor for team repository records.
    model = Repository
    extra = 1


class ContactChannelInline(admin.TabularInline):
    # Inline editor for team contact channels.
    model = ContactChannel
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    # Core admin configuration for the Team registry.
    list_display = ('name', 'department', 'manager', 'team_type', 'status', 'is_active')
    list_filter = ('department', 'team_type', 'status', 'is_active')
    search_fields = ('name', 'mission', 'description', 'manager__username', 'manager__first_name', 'manager__last_name')
    filter_horizontal = ('skills',)
    inlines = (TeamMemberInline, RepositoryInline, ContactChannelInline)


admin.site.register(TeamType)
admin.site.register(TeamDependency)
admin.site.register(TeamMember)
admin.site.register(Repository)
admin.site.register(SoftwareProduct)
admin.site.register(ContactChannel)
admin.site.register(Skill)
admin.site.register(AuditTrail)
admin.site.register(TeamEmail)
