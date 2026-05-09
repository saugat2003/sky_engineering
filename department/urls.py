"""URL routes for department views.

Author: Rupesh Dahal"""

from django.urls import path
from . import views
urlpatterns = [
    path("", views.department_overview, name="depertment_overview" ),
    path("new/", views.department_create, name="department_create" ),
    path("<int:id>/", views.department_detail, name="depertment_detail" ),
    path("org-chart/", views.org_chart, name="org_chart" )
]
