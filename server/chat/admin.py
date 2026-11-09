from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Feedback, Message, User
from .moderation.labels import NON_TOXIC


class FlaggedMessagesInline(admin.TabularInline):
    model = Message
    fk_name = "sender"
    verbose_name_plural = "flagged messages"
    extra = 0
    can_delete = False
    fields = ("timestamp", "receiver", "original_content", "toxicity_label", "toxicity_score")
    readonly_fields = fields

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(toxicity_label=NON_TOXIC).order_by("-timestamp")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "toxic_message_count", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff")
    search_fields = ("username", "email")
    ordering = ("-toxic_message_count", "username")
    readonly_fields = ("toxic_message_count",)
    fieldsets = BaseUserAdmin.fieldsets + (("Chat", {"fields": ("profile_photo", "toxic_message_count")}),)
    inlines = [FlaggedMessagesInline]


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
    list_display = ("timestamp", "sender", "receiver", "original_content", "toxicity_label", "toxicity_score", "classifier")
    list_filter = (ToxicityFilter, "toxicity_label", "classifier", "timestamp")
    search_fields = ("sender__username", "receiver__username", "original_content")
    readonly_fields = ("sender", "receiver", "content", "original_content", "toxicity_score", "classifier", "timestamp")
    date_hierarchy = "timestamp"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("created_at", "feedback")
    search_fields = ("feedback",)
    readonly_fields = ("feedback", "created_at")
