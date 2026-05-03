from django.urls import path
from . import views
urlpatterns = [
    path("", views.department_overview, name="depertment_overview" )
]
