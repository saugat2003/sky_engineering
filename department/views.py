"""Department app views.

Author: Rupesh Dahal
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from department.forms import DepartmentForm
from department.models import Department
from teams.models import Team, TeamDependency, TeamMember


@login_required
def department_overview(request):
    """Render the department overview dashboard.

    Args:
        request: Django HTTP request.

    Returns:
        HttpResponse with the department overview page.
    """
    total_department = Department.objects.all().count()
    total_active_teams = Team.objects.filter(status="active").count()
    total_engineers = TeamMember.objects.all().count()

    departments = Department.objects.annotate(
        total_teams = Count("teams", distinct=True),
        total_members = Count("teams__members__user", distinct=True)
    )

    context = {
        "total_department": total_department,
        "total_active_teams": total_active_teams,
        "total_engineers": total_engineers,
        "departments": departments
    }
    return render(request, "department/overview.html", context=context)


@login_required
@user_passes_test(lambda user: user.is_staff)
def department_create(request):
    """Create a new department.

    Args:
        request: Django HTTP request.

    Returns:
        HttpResponse with the form or a redirect on success.
    """
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f"{department.name} department was created.")
            return redirect("depertment_detail", id=department.id)
    else:
        form = DepartmentForm()

    return render(request, "department/department_form.html", {"form": form})


@login_required
def department_detail(request, id):
    """Render details for a single department.

    Args:
        request: Django HTTP request.
        id: Department primary key.

    Returns:
        HttpResponse with the department detail page.
    """
    department = get_object_or_404(Department.objects.prefetch_related(
        'teams',
        'teams__team_type',
        'teams__manager',
        'teams__downstream_dependencies__to_team',
        'teams__upstream_dependencies__from_team',
    ), id=id)
    context = {
        "department": department
    }
    return render(request, "department/department_detail.html", context=context )


@login_required
def org_chart(request):
    """Render the organization chart view.

    Args:
        request: Django HTTP request.

    Returns:
        HttpResponse with the org chart page.
    """
    departments = Department.objects.annotate(
        total_teams=Count("teams", distinct=True),
        total_members=Count("teams__members__user", distinct=True)
    ).prefetch_related('teams', 'teams__manager')

    dependencies = TeamDependency.objects.select_related(
        'from_team',
        'from_team__department',
        'from_team__team_type',
        'to_team',
        'to_team__department',
        'to_team__team_type',
    )

    context = {
        "departments": departments,
        "dependencies": dependencies,
    }
    return render(request, "department/org_chart.html", context=context)
