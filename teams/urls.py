# Authorship: Teams module implementation led by Saugat Bhattarai (0xsaugat).
from django.urls import path

from . import views

urlpatterns = [
    path("", views.team_list, name="team_list"),
    path("new/", views.team_create, name="team_create"),
    path("search/", views.team_search, name="team_search"),
    path("<int:pk>/", views.team_detail, name="team_detail"),
    path("<int:pk>/email/", views.team_email, name="team_email"),
    path("<int:pk>/dependencies/", views.team_dependencies, name="team_dependencies"),
    path("<int:pk>/skills/", views.team_skills, name="team_skills"),
    path("<int:pk>/schedule/", views.schedule_team_meeting, name="team_schedule"),
]
