"""The Django admin, branded as SafeChat, with a moderation dashboard on its front page."""

from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.utils import timezone

from .moderation.labels import LABELS, NON_TOXIC

SEVERE = {"threat", "identity hate", "severe toxic"}


def label_kind(label):
    """Colour group for a label, shared with the chat app: ok, warn or severe."""
    if label == NON_TOXIC:
        return "ok"
    return "severe" if label in SEVERE else "warn"


def moderation_stats():
    from django.contrib.auth import get_user_model

    from .models import Feedback, Message

    User = get_user_model()
    messages = Message.objects.all()
    flagged = messages.exclude(toxicity_label=NON_TOXIC)
    total, flagged_count = messages.count(), flagged.count()

    by_label = []
    for label in [label for label in LABELS if label != NON_TOXIC]:
        count = flagged.filter(toxicity_label=label).count()
        by_label.append(
            {"label": label, "count": count, "kind": label_kind(label), "width": round(100 * count / flagged_count) if flagged_count else 0}
        )

    return {
        "messages": total,
        "today": messages.filter(timestamp__gte=timezone.now() - timedelta(days=1)).count(),
        "flagged": flagged_count,
        "flagged_pct": round(100 * flagged_count / total) if total else 0,
        "users": User.objects.count(),
        "users_flagged": User.objects.filter(toxic_message_count__gt=0).count(),
        "feedback": Feedback.objects.count(),
        "by_label": by_label,
        "recent_flagged": [
            {"message": m, "kind": label_kind(m.toxicity_label)}
            for m in flagged.select_related("sender", "receiver").order_by("-timestamp", "-id")[:6]
        ],
        "top_users": User.objects.filter(toxic_message_count__gt=0).order_by("-toxic_message_count", "username")[:5],
    }


class ModerationAdminSite(admin.AdminSite):
    site_header = "SafeChat"
    site_title = "SafeChat admin"
    index_title = "Moderation"

    def index(self, request, extra_context=None):
        return super().index(request, {"stats": moderation_stats(), **(extra_context or {})})


class ModerationAdminConfig(AdminConfig):
    default_site = "chat.admin_site.ModerationAdminSite"
