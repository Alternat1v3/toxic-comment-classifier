from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.text import Truncator

from .admin_site import label_kind
from .models import Feedback, Message, User
from .moderation.labels import NON_TOXIC


def label_badge(message):
    score = f" · {round(message.toxicity_score * 100)}%" if message.toxicity_score is not None else ""
    return format_html('<span class="sc-badge sc-badge--{}">{}{}</span>', label_kind(message.toxicity_label), message.toxicity_label, score)


class FlaggedMessagesInline(admin.TabularInline):
    model = Message
    fk_name = "sender"
    verbose_name_plural = "flagged messages"
    extra = 0
    can_delete = False
    fields = ("timestamp", "receiver", "original_content", "label")
    readonly_fields = fields

    @admin.display(description="Label")
    def label(self, message):
        return label_badge(message)

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(toxicity_label=NON_TOXIC).order_by("-timestamp")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "flagged", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff")
    search_fields = ("username", "email")
    ordering = ("-toxic_message_count", "username")
    readonly_fields = ("toxic_message_count",)
    fieldsets = BaseUserAdmin.fieldsets + (("Chat", {"fields": ("profile_photo", "toxic_message_count")}),)
    inlines = [FlaggedMessagesInline]

    @admin.display(description="Flagged messages", ordering="toxic_message_count")
    def flagged(self, user):
        if not user.toxic_message_count:
            return format_html('<span class="sc-muted">none</span>')
        return format_html('<span class="sc-badge sc-badge--warn">{} flagged</span>', user.toxic_message_count)


class ToxicityFilter(admin.SimpleListFilter):
    title = "flagged"
    parameter_name = "flagged"

    def lookups(self, request, model_admin):
        return [("yes", "Flagged"), ("no", "Not flagged")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(toxicity_label=NON_TOXIC)
        if self.value() == "no":
            return queryset.filter(toxicity_label=NON_TOXIC)
        return queryset


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "sender", "receiver", "typed", "label", "classifier")
    list_display_links = ("timestamp", "typed")
    list_filter = (ToxicityFilter, "toxicity_label", "classifier", "timestamp")
    search_fields = ("sender__username", "receiver__username", "original_content")
    readonly_fields = ("sender", "receiver", "content", "original_content", "toxicity_score", "classifier", "timestamp")
    date_hierarchy = "timestamp"
    list_select_related = ("sender", "receiver")

    @admin.display(description="What was typed")
    def typed(self, message):
        return Truncator(message.original_content or message.content).chars(70)

    @admin.display(description="Label", ordering="toxicity_label")
    def label(self, message):
        return label_badge(message)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("created_at", "feedback")
    search_fields = ("feedback",)
    readonly_fields = ("feedback", "created_at")
