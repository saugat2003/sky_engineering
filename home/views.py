from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from accounts.models import UserProfile


@login_required
def home_redirect(request):
    return render(request, 'home/dashboard.html')


@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user_id=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.save()

            profile.phone = request.POST.get('phone', '').strip()
            profile.bio = request.POST.get('bio', '').strip()
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()

            messages.success(request, 'Profile updated successfully.')

        elif form_type == 'password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password updated successfully.')
            else:
                for field_errors in password_form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)
            return redirect('profile')

        return redirect('profile')

    context = {
        'profile': profile,
        'password_form': PasswordChangeForm(user),
    }
    return render(request, 'home/profile.html', context)
