# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser, Message


# class CustomUserAdmin(UserAdmin):
#     list_display = ("username", "email", "is_staff", "is_active", "date_joined")
#     search_fields = ("username", "email")
#     list_filter = ("is_staff", "is_active")


# admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Message)
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser, Message


# class CustomUserAdmin(UserAdmin):
#     list_display = (
#         "username",
#         "email",
#         "is_staff",
#         "is_active",
#         "date_joined",
#         "toxic_word_count",
#     )
#     search_fields = ("username", "email")
#     list_filter = ("is_staff", "is_active")
#     readonly_fields = ("toxic_word_count",)

#     # Add toxic messages in the admin detail view of each user
#     def toxic_messages(self, obj):
#         messages = Message.objects.filter(
#             sender=obj,
#             toxicity_label__in=[
#                 "toxic",
#                 "severe toxic",
#                 "obscene",
#                 "threat",
#                 "insult",
#                 "identity hate",
#             ],
#         )
#         return "\n".join([f"{msg.content} ({msg.toxicity_label})" for msg in messages])

#     toxic_messages.short_description = "Toxic Messages"

#     fieldsets = UserAdmin.fieldsets + (
#         (None, {"fields": ("toxic_word_count", "toxic_messages")}),
#     )


# class MessageAdmin(admin.ModelAdmin):
#     list_display = ("sender", "receiver", "content", "timestamp", "toxicity_label")
#     search_fields = ("sender__username", "receiver__username", "content")
#     list_filter = ("toxicity_label", "timestamp")


# admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Message, MessageAdmin)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Message, Feedback


class ToxicMessagesInline(admin.TabularInline):
    model = Message
    fk_name = "sender"
    extra = 0
    fields = ("receiver", "content", "toxicity_label", "timestamp")
    readonly_fields = ("receiver", "content", "toxicity_label", "timestamp")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.filter(
            toxicity_label__in=[
                "toxic",
                "severe toxic",
                "obscene",
                "threat",
                "insult",
                "identity hate",
            ]
        )


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
        "toxic_word_count",
    )
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active")
    inlines = [ToxicMessagesInline]

    readonly_fields = ("toxic_word_count",)

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("toxic_word_count",)}),)


class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "content", "timestamp", "toxicity_label")
    search_fields = ("sender__username", "receiver__username", "content")
    list_filter = ("toxicity_label", "timestamp")


class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "feedback",
        "created_at",
    )  # Fields to display in the admin list view
    search_fields = (
        "feedback",
        "user__username",
    )  # Enable searching by feedback text or username
    list_filter = ("created_at", "user")  # Filter feedback by user and creation date
    ordering = ("-created_at",)  # Order feedback by creation date (latest first)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Feedback, FeedbackAdmin)
