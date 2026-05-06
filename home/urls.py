from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("notifications/mark-read/", views.mark_notifications_read, name="notifications_mark_read"),
]
