from __future__ import annotations

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import MessageComposeForm, MessageReplyForm
from .models import Message


def _parse_date(value: str | None):
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _ensure_access(user: User, message: Message) -> None:
    is_sender = message.sender_id == user.id
    is_recipient = message.recipient_id == user.id
    if not (is_sender or is_recipient):
        raise Http404()

    if message.status == Message.Status.DRAFT and not is_sender:
        raise Http404()


def _apply_filters(request: HttpRequest, qs):
    q = (request.GET.get("q") or "").strip()
    sender = (request.GET.get("sender") or "").strip()
    subject = (request.GET.get("subject") or "").strip()
    date_from = _parse_date(request.GET.get("from"))
    date_to = _parse_date(request.GET.get("to"))

    if q:
        qs = qs.filter(
            Q(subject__icontains=q)
            | Q(body__icontains=q)
            | Q(sender__username__icontains=q)
            | Q(sender__email__icontains=q)
            | Q(sender__first_name__icontains=q)
            | Q(sender__last_name__icontains=q)
            | Q(recipient__username__icontains=q)
            | Q(recipient__email__icontains=q)
        )

    if sender:
        qs = qs.filter(
            Q(sender__username__icontains=sender)
            | Q(sender__email__icontains=sender)
            | Q(sender__first_name__icontains=sender)
            | Q(sender__last_name__icontains=sender)
        )

    if subject:
        qs = qs.filter(subject__icontains=subject)

    if date_from:
        qs = qs.filter(
            Q(sent_at__date__gte=date_from)
            | Q(sent_at__isnull=True, created_at__date__gte=date_from)
        )
    if date_to:
        qs = qs.filter(
            Q(sent_at__date__lte=date_to)
            | Q(sent_at__isnull=True, created_at__date__lte=date_to)
        )

    return qs


@login_required
def inbox(request: HttpRequest) -> HttpResponse:
    qs = Message.objects.select_related("sender", "recipient").filter(
        recipient=request.user, status=Message.Status.INBOX
    )
    qs = _apply_filters(request, qs)
    return render(
        request,
        "messaging/mailbox.html",
        {
            "mailbox": "inbox",
            "messages_list": qs,
        },
        status=200,
    )


@login_required
def sent(request: HttpRequest) -> HttpResponse:
    qs = Message.objects.select_related("sender", "recipient").filter(
        sender=request.user, status=Message.Status.SENT
    )
    qs = _apply_filters(request, qs)
    return render(
        request,
        "messaging/mailbox.html",
        {
            "mailbox": "sent",
            "messages_list": qs,
        },
        status=200,
    )


@login_required
def drafts(request: HttpRequest) -> HttpResponse:
    qs = Message.objects.select_related("sender", "recipient").filter(
        sender=request.user, status=Message.Status.DRAFT
    )
    qs = _apply_filters(request, qs)
    return render(
        request,
        "messaging/mailbox.html",
        {
            "mailbox": "drafts",
            "messages_list": qs,
        },
        status=200,
    )


@login_required
def detail(request: HttpRequest, message_id: int) -> HttpResponse:
    message_obj = get_object_or_404(
        Message.objects.select_related("sender", "recipient", "parent_message"),
        id=message_id,
    )
    _ensure_access(request.user, message_obj)

    if message_obj.status == Message.Status.INBOX and message_obj.recipient_id == request.user.id:
        if not message_obj.is_read:
            Message.objects.filter(id=message_obj.id).update(is_read=True)
            message_obj.is_read = True

    reply_form = MessageReplyForm()

    return render(
        request,
        "messaging/detail.html",
        {
            "message_obj": message_obj,
            "reply_form": reply_form,
        },
        status=200,
    )


@transaction.atomic
def _create_delivery(sender: User, recipient: User, subject: str, body: str, parent: Message | None = None):
    now = timezone.now()
    # recipient copy
    inbox_copy = Message.objects.create(
        sender=sender,
        recipient=recipient,
        subject=subject or "",
        body=body,
        status=Message.Status.INBOX,
        is_read=False,
        parent_message=parent,
        sent_at=now,
    )
    # sender copy
    sent_copy = Message.objects.create(
        sender=sender,
        recipient=recipient,
        subject=subject or "",
        body=body,
        status=Message.Status.SENT,
        is_read=True,
        parent_message=parent,
        sent_at=now,
    )
    return inbox_copy, sent_copy


@login_required
def compose(request: HttpRequest) -> HttpResponse:
    initial = {}
    to = (request.GET.get("to") or "").strip()
    subject = (request.GET.get("subject") or "").strip()
    parent_id = request.GET.get("parent")
    if to:
        initial["to"] = to
    if subject:
        initial["subject"] = subject

    if request.method == "POST":
        form = MessageComposeForm(request.POST)
        action = (request.POST.get("action") or "").strip()
        if form.is_valid():
            recipient = form.cleaned_data["to"]
            subj = form.cleaned_data.get("subject") or ""
            body = form.cleaned_data["body"]

            parent = None
            if parent_id:
                try:
                    parent = Message.objects.get(id=int(parent_id))
                    _ensure_access(request.user, parent)
                except Exception:
                    parent = None

            if action == "draft":
                Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    subject=subj,
                    body=body,
                    status=Message.Status.DRAFT,
                    is_read=True,
                    parent_message=parent,
                )
                messages.success(request, "Draft saved.")
                return redirect("messages_drafts")

            _create_delivery(request.user, recipient, subj, body, parent=parent)
            messages.success(request, "Message sent.")
            return redirect("messages_sent")
    else:
        form = MessageComposeForm(initial=initial)

    return render(
        request,
        "messaging/compose.html",
        {
            "form": form,
        },
        status=200,
    )


@login_required
def reply(request: HttpRequest, message_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("messages_detail", message_id=message_id)

    original = get_object_or_404(Message.objects.select_related("sender", "recipient"), id=message_id)
    _ensure_access(request.user, original)

    form = MessageReplyForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Reply cannot be empty.")
        return redirect("messages_detail", message_id=message_id)

    # Reply goes to the other participant.
    if request.user.id == original.sender_id:
        recipient = original.recipient
    else:
        recipient = original.sender

    subject = original.subject or ""
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}".strip()

    _create_delivery(request.user, recipient, subject, form.cleaned_data["body"], parent=original)
    messages.success(request, "Reply sent.")
    return redirect("messages_sent")


@login_required
def delete(request: HttpRequest, message_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("messages_detail", message_id=message_id)

    message_obj = get_object_or_404(Message, id=message_id)
    _ensure_access(request.user, message_obj)

    # Soft delete only this copy (inbox/sent/draft are separate rows).
    Message.objects.filter(id=message_obj.id).update(status=Message.Status.DELETED)
    messages.success(request, "Message deleted.")

    # Redirect back to the appropriate mailbox.
    if message_obj.status == Message.Status.DRAFT:
        return redirect("messages_drafts")
    if message_obj.sender_id == request.user.id and message_obj.status == Message.Status.SENT:
        return redirect("messages_sent")
    return redirect("messages_inbox")


@login_required
def send_draft(request: HttpRequest, message_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("messages_detail", message_id=message_id)

    draft = get_object_or_404(Message.objects.select_related("recipient"), id=message_id)
    _ensure_access(request.user, draft)

    if draft.status != Message.Status.DRAFT or draft.sender_id != request.user.id:
        raise Http404()

    _create_delivery(request.user, draft.recipient, draft.subject, draft.body, parent=draft.parent_message)
    Message.objects.filter(id=draft.id).update(status=Message.Status.DELETED)
    messages.success(request, "Draft sent.")
    return redirect("messages_sent")
