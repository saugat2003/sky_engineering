

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from accounts.forms import RegisterForm


# Create your views here.
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form}, status=200)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    context = {}

    if request.method == "POST":
        identifier = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""

        context["email"] = identifier

        if not identifier or not password:
            context["error"] = "Email/username and password are required."
        else:
            username_candidate = identifier

            if "@" in identifier:
                try:
                    username_candidate = User.objects.get(email__iexact=identifier).username
                except User.DoesNotExist:
                    username_candidate = identifier

            user = authenticate(request, username=username_candidate, password=password)

            if user is None:
                user = authenticate(request, email=identifier, password=password)

            if user is not None:
                login(request, user)
                return redirect("dashboard")

            context["error"] = "Invalid email/username or password."

    return render(request, "auth/login.html", context, status=200)


def logout_view(request):
    return render(request, "auth/logout.html", status=200)