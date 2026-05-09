from django.contrib import admin

from messaging.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ("subject", "sender", "recipient", "status", "is_read", "sent_at", "created_at")
	list_filter = ("status", "is_read", "sent_at", "created_at")
	search_fields = (
		"subject",
		"body",
		"sender__username",
		"sender__email",
		"recipient__username",
		"recipient__email",
	)
	autocomplete_fields = ("sender", "recipient", "parent_message")
	list_select_related = ("sender", "recipient", "parent_message")
