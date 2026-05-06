from scheduling.models import Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {'unread_notification_count': 0, 'recent_notifications': []}
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    recent = list(Notification.objects.filter(user=request.user)[:8])
    return {'unread_notification_count': unread_count, 'recent_notifications': recent}
