from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .moderation.labels import LABELS, NON_TOXIC


class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)
    toxic_message_count = models.PositiveIntegerField(default=0, help_text="Messages this user sent that were flagged.")


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField(help_text="What the other person sees, with offensive words replaced.")
    original_content = models.TextField(blank=True, help_text="What the sender typed, for moderators.")
    toxicity_label = models.CharField(max_length=20, choices=[(label, label) for label in LABELS], default=NON_TOXIC)
    toxicity_score = models.FloatField(null=True, blank=True, help_text="Model confidence for the label, 0 to 1.")
    classifier = models.CharField(max_length=10, blank=True, help_text="'bert' or 'keywords'.")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["timestamp", "id"]
        indexes = [models.Index(fields=["sender", "receiver", "timestamp"])]

    @property
    def is_toxic(self):
        return self.toxicity_label != NON_TOXIC

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content[:50]}"


class Feedback(models.Model):
    """Anonymous feedback about the app. The sender is deliberately not stored."""

    feedback = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "feedback"

    def __str__(self):
        return self.feedback[:60]
