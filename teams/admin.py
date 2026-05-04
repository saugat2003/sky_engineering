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
    model = TeamMember
    extra = 1


class RepositoryInline(admin.TabularInline):
    model = Repository
    extra = 1


class ContactChannelInline(admin.TabularInline):
    model = ContactChannel
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
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
