from django.contrib import admin

from teams.models import Team, TeamMember, TeamType

# Register your models here.
admin.site.register(TeamType)
admin.site.register(Team)
admin.site.register(TeamMember)