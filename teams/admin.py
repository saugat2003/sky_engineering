from django.contrib import admin

from teams.models import Team, TeamDependency, TeamMember, TeamType

# Register your models here.
admin.site.register(TeamType)
admin.site.register(Team)
admin.site.register(TeamDependency)
admin.site.register(TeamMember)
