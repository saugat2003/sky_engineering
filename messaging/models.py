from django.conf import settings
from django.db import models
from django.utils import timezone


class Message(models.Model):
    class Status(models.TextChoices):
        INBOX = "inbox", "Inbox"
        SENT = "sent", "Sent"
        DRAFT = "draft", "Draft"
        DELETED = "deleted", "Deleted"

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_received",
    )
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INBOX)
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sender", "status"]),
            models.Index(fields=["recipient", "status"]),
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self) -> str:
        return f"Message({self.id}) {self.sender} -> {self.recipient}: {self.subject}"

    @property
    def display_timestamp(self):
        return self.sent_at or self.created_at

    def mark_sent(self):
        self.status = self.Status.SENT
        self.sent_at = self.sent_at or timezone.now()
