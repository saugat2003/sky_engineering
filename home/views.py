from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home_redirect(request):
    return render(request, 'home/dashboard.html')
