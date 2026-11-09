from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect
from rest_framework import status, serializers
from .models import CustomUser, Feedback
from .serializers import UsersSerializer, FeedbackSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from rest_framework import generics
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Message
from .serializers import MessageSerializer
from django.db.models import Q
from channels.db import database_sync_to_async
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import math


class RegisteredUsersAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer


class RegistrationAPIView(APIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def post(self, request):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return Response(
                {"message": f"Account created for {user.username}!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )


# class LoginAPIView(APIView):

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data["username"]
#             password = serializer.validated_data["password"]

#             user = authenticate(request, username=username, password=password)
#             if user is not None:

#                 login(request, user)
#                 return Response(
#                     {"message": f"Login successful. Welcome {user.username}"},
#                     status=status.HTTP_200_OK,
#                 )
#             else:
#                 return Response(
#                     {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
#                 )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    def post(self, request):
        django_logout(request)
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )

    def get(self, request):
        django_logout(request)
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class CheckLoginStatus(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({"loggedIn": True}, status=status.HTTP_200_OK)
        return Response({"loggedIn": False}, status=status.HTTP_401_UNAUTHORIZED)


User = get_user_model()


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        contact_username = self.kwargs["contact_username"]
        return Message.objects.filter(
            (Q(sender=current_user) & Q(receiver__username=contact_username))
            | (Q(sender__username=contact_username) & Q(receiver=current_user))
        ).order_by("timestamp")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@database_sync_to_async
def save_message(self, sender, receiver, content):
    sender_user = CustomUser.objects.get(username=sender)
    receiver_user = CustomUser.objects.get(username=receiver)
    Message.objects.create(sender=sender_user, receiver=receiver_user, content=content)


class PreprocessedMessagesAPIView(APIView):
    def get(self, request):
        df = pd.read_csv("preprocessed_chat_data.csv")
        data = df.to_dict(orient="records")
        return Response(data, status=status.HTTP_200_OK)


nltk.download("stopwords")

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()


def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.lower()
    text = " ".join(word for word in text.split() if word not in stop_words)
    text = " ".join(stemmer.stem(word) for word in text.split())
    return text


class PreprocessedMessagesAPIView(APIView):
    def get(self, request):
        messages = Message.objects.all()
        preprocessed_messages = []

        for message in messages:
            if (
                message.content is None
                or isinstance(message.content, float)
                and (math.isnan(message.content) or math.isinf(message.content))
            ):
                preprocessed_content = ""
            else:
                preprocessed_content = preprocess_text(message.content)

            preprocessed_messages.append(
                {
                    "sender": message.sender.username,
                    "receiver": message.receiver.username,
                    "original_content": message.content,
                    "preprocessed_content": preprocessed_content,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return Response(preprocessed_messages)


from django.middleware.csrf import get_token


class GetCSRFTokenAPIView(APIView):
    def get(self, request):
        csrf_token = get_token(request)
        return Response({"csrf_token": csrf_token})


class FeedbackView(APIView):
    def post(self, request, *args, **kwargs):
        # Ensure the user is logged in or handle anonymous feedback
        user = request.user if request.user.is_authenticated else None
        feedback_data = request.data.get("feedback")

        if not feedback_data:
            return Response(
                {"error": "Feedback cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        feedback = Feedback.objects.create(user=user, feedback=feedback_data)
        serializer = FeedbackSerializer(feedback)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


from django.contrib.auth import logout


def app_logout(request):

    logout(request)
    request.session.flush()
    return redirect("login")
