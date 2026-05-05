"""URL configuration for scheduling app."""

from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    # Meeting management
    path('create/', views.schedule_meeting, name='schedule_meeting_create'),
    path('<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('<int:pk>/edit/', views.edit_meeting, name='meeting_edit'),
    path('<int:pk>/cancel/', views.cancel_meeting, name='meeting_cancel'),
    
    # Calendar views
    path('calendar/month/', views.monthly_calendar, name='calendar_month'),
    path('calendar/week/', views.weekly_calendar, name='calendar_week'),
    
    # Upcoming meetings
    path('upcoming/', views.upcoming_schedules, name='upcoming_schedules'),
]
