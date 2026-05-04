from django.shortcuts import render
from django.db.models import Count
from department.models import Department
from teams.models import Team, TeamMember

# Create your views here.
def department_overview(request):
    
    total_department = Department.objects.all().count()
    total_active_teams = Team.objects.filter(status="active").count()
    total_engineers = TeamMember.objects.all().count()

    departments = Department.objects.annotate(
        total_teams = Count("teams", distinct=True),
        total_members = Count("teams__members__user", distinct=True)
    )

    # for dept in departments:
    #     print("Department:", dept.name)
    #     print("Total Teams:", dept.total_teams)
    #     print("Total Members:", dept.total_members)
    #     print("-" * 30)

    context = {
        "total_department": total_department,
        "total_active_teams": total_active_teams,
        "total_engineers": total_engineers,
        "departments": departments
    }
    return render(request, "department/overview.html", context=context)


def department_detail(request, id):
    department = Department.objects.get(id=id)
    context = {
        "department": department
    }
    return render(request, "department/department_detail.html", context=context )


def org_chart(request):
    departments = Department.objects.annotate(
        total_teams=Count("teams", distinct=True),
        total_members=Count("teams__members__user", distinct=True)
    ).prefetch_related('teams', 'teams__manager')

    context = {
        "departments": departments
    }
    return render(request, "department/org_chart.html", context=context)