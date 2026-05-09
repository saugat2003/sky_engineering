"""URL routes for the messaging app.
Author: Kaushik Singh Bhandari
"""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.inbox, name="messages_inbox"),
    path("inbox/", views.inbox, name="messages_inbox"),
    path("sent/", views.sent, name="messages_sent"),
    path("drafts/", views.drafts, name="messages_drafts"),
    path("new/", views.compose, name="messages_compose"),
    path("<int:message_id>/", views.detail, name="messages_detail"),
    path("<int:message_id>/reply/", views.reply, name="messages_reply"),
    path("<int:message_id>/delete/", views.delete, name="messages_delete"),
    path("<int:message_id>/draft/send/", views.send_draft, name="messages_send_draft"),
]
