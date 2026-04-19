from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="home_redirect"), 
    path("/dashboard", views.dashboard, name="dashboard"), 
    
]
