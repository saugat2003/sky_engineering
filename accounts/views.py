from django.shortcuts import render

# Create your views here.
def register(request):
    return render(request, "auth/register.html", status=200)


def login(request):
    return render(request, "auth/login.html", status=200)

def logout(request):
    return render(request, "auth/logout.html", status=200)