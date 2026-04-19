

"""Authentication views for registration, login, and logout flows."""

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from accounts.forms import RegisterForm


# Create your views here.
def register_view(request):
    """Render and process the user registration form."""

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form}, status=200)


def login_view(request):
    """Authenticate users by username or email and start a session."""

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
    """Log out the current user and redirect to the login page."""

    logout(request)
    return redirect("login")