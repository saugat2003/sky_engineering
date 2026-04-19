from django.shortcuts import redirect, render
from django.views import View

# Create your views here.
def home_redirect(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    return redirect("login")

def dashboard(request):
    return render(request, 'home/dashboard.html')


