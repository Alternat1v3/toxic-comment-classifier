from rest_framework import serializers
from .models import CustomUser, Message, Feedback


class UsersSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False)
    toxic_messages = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "profile_photo",
            "toxic_word_count",
            "toxic_messages",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def get_toxic_messages(self, obj):
        messages = obj.toxic_messages.all()
        return [
            {"content": msg.content, "toxicity_label": msg.toxicity_label}
            for msg in messages
        ]

    def create(self, validated_data):
        profile_photo = validated_data.pop("profile_photo", None)
        user = CustomUser.objects.create_user(**validated_data)
        if profile_photo:
            user.profile_photo = profile_photo
            user.save()
        return user


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["sender", "receiver", "content", "timestamp", "toxicity_label"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "feedback", "user", "created_at"]


# EXTRA CODE
# from rest_framework import serializers
# from .models import CustomUser


# class UsersSerializer(serializers.ModelSerializer):
#     profile_photo = serializers.ImageField(required=False)  # Add profile photo field

#     class Meta:
#         model = CustomUser
#         fields = ["username", "email", "password", "profile_photo"]
#         extra_kwargs = {
#             "password": {"write_only": True}
#         }

#     def create(self, validated_data):
#         profile_photo = validated_data.pop(
#             "profile_photo", None
#         )
#         user = CustomUser.objects.create_user(**validated_data)
#         if profile_photo:
#             user.profile_photo = profile_photo  # Save profile photo
#             user.save()
#         return user


# class UsersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ["username", "email", "password"]
#         extra_kwargs = {
#             "password": {"write_only": True}
#         }

#     def create(self, validated_data):
#         user = CustomUser.objects.create_user(**validated_data)
#         return user
