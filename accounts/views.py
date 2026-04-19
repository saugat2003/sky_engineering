from django.shortcuts import redirect, render

# Create your views here.
def register(request):
    return render(request, "auth/register.html", status=200)


def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "auth/login.html", status=200)

def logout(request):
    return render(request, "auth/logout.html", status=200)