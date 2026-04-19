

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from accounts.forms import RegisterForm


# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form}, status=200)


def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, "auth/login.html", status=404 )
        
        user = authenticate(email=email, password=password)
    return render(request, "auth/login.html", status=200)

def logout(request):
    return render(request, "auth/logout.html", status=200)