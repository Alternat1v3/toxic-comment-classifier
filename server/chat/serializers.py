from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Feedback, Message

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "email", "password", "profile_photo"]
        extra_kwargs = {"profile_photo": {"required": False}}

    def validate(self, attrs):
        validate_password(attrs["password"], User(username=attrs.get("username"), email=attrs.get("email")))
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})


class MeSerializer(serializers.ModelSerializer):
    """The signed-in user's own profile."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile_photo", "toxic_message_count"]


class ContactSerializer(serializers.ModelSerializer):
    """Other users, as shown in the contact list. No emails or moderation data."""

    class Meta:
        model = User
        fields = ["id", "username", "profile_photo"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source="sender.username")
    message = serializers.CharField(source="content")

    class Meta:
        model = Message
        fields = ["id", "sender", "message", "timestamp", "toxicity_label", "toxicity_score"]


class ModerationCheckSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1000, trim_whitespace=True)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "feedback", "created_at"]
        read_only_fields = ["id", "created_at"]
