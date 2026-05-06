from scheduling.models import Notification
from accounts.models import UserProfile


def notifications(request):
    if not request.user.is_authenticated:
        return {'unread_notification_count': 0, 'recent_notifications': []}
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    recent = list(Notification.objects.filter(user=request.user)[:8])
    return {'unread_notification_count': unread_count, 'recent_notifications': recent}


def current_profile(request):
    if not request.user.is_authenticated:
        return {'current_profile': None}

    profile = UserProfile.objects.filter(user_id=request.user).first()
    return {'current_profile': profile}
