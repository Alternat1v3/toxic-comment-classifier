from django.db import models
from django.contrib.auth.models import AbstractUser, User


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    groups = models.ManyToManyField("auth.Group", related_name="custom_user_groups")
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_permissions"
    )
    profile_photo = models.ImageField(
        upload_to="profile_photos/", null=True, blank=True
    )
    toxic_word_count = models.IntegerField(default=0)
    toxic_messages = models.ManyToManyField("Message", related_name="toxic_messages")

    def increment_toxic_count(self, count, message):
        self.toxic_word_count += count
        self.toxic_messages.add(message)
        self.save()


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    toxicity_label = models.CharField(max_length=50, default="non-toxic")

    def __str__(self):
        return f"{self.sender} to {self.receiver} : {self.content}"


class Feedback(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )  # Optional - to link feedback to a user
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Anonymous'}"


# from django.db import models
# from django.contrib.auth.models import AbstractUser


# class CustomUser(AbstractUser):
#     email = models.EmailField(max_length=255, unique=True)
#     groups = models.ManyToManyField("auth.Group", related_name="custom_user_groups")
#     user_permissions = models.ManyToManyField(
#         "auth.Permission", related_name="custom_user_permissions"
#     )
