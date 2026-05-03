from django.shortcuts import render

# Create your views here.
def department_overview(request):
    return render(request, "department/overview.html")
