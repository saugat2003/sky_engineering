"""URL routes for the home app.
Author: Saugat Bhattarai and Rupesh Dahal
"""

from django.urls import path
from . import views

urlpatterns = [
    path("terms/", views.terms_view, name="terms"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("", views.home_redirect, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("notifications/mark-read/", views.mark_notifications_read, name="notifications_mark_read"),
]
