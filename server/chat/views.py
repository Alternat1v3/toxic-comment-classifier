from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feedback, Message
from .moderation import classifier_status
from .moderation.pipeline import moderate
from .serializers import (
    ContactSerializer,
    FeedbackSerializer,
    LoginSerializer,
    MeSerializer,
    MessageSerializer,
    ModerationCheckSerializer,
    RegisterSerializer,
)

User = get_user_model()


class SessionAuthenticationWithCsrf(SessionAuthentication):
    """
    DRF only checks the CSRF token for signed-in users. Sign-in and sign-up need it too,
    or another site could sign a visitor into the attacker's account ("login CSRF").
    """

    def authenticate(self, request):
        self.enforce_csrf(request)
        return super().authenticate(request)


@method_decorator(ensure_csrf_cookie, name="get")
class CsrfView(APIView):
    """Sets the CSRF cookie the frontend sends back with every POST."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    authentication_classes = [SessionAuthenticationWithCsrf]
    permission_classes = [AllowAny]
    throttle_scope = "auth"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(MeSerializer(user, context={"request": request}).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = [SessionAuthenticationWithCsrf]
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response({"detail": "Wrong username or password."}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response(MeSerializer(user, context={"request": request}).data)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class ContactListView(generics.ListAPIView):
    serializer_class = ContactSerializer
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(is_active=True).exclude(pk=self.request.user.pk).order_by("username")


class ConversationView(generics.ListAPIView):
    """Messages between the signed-in user and one other user, oldest first."""

    serializer_class = MessageSerializer
    pagination_class = None

    def get_queryset(self):
        me = self.request.user
        other = get_object_or_404(User, username=self.kwargs["username"])
        return (
            Message.objects.filter(Q(sender=me, receiver=other) | Q(sender=other, receiver=me))
            .select_related("sender")
            .order_by("-timestamp", "-id")[:200]
        )

    def list(self, request, *args, **kwargs):
        messages = list(self.get_queryset())[::-1]
        return Response(self.get_serializer(messages, many=True).data)


class ModerationCheckView(APIView):
    """Runs a piece of text through the same moderation as chat messages, without sending it."""

    throttle_scope = "moderation"

    def post(self, request):
        serializer = ModerationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = moderate(serializer.validated_data["text"])
        prediction = result.prediction
        return Response(
            {
                "label": prediction.label,
                "score": prediction.score,
                "is_toxic": prediction.is_toxic,
                "scores": prediction.scores,
                "source": prediction.source,
                "shown_as": result.shown,
            }
        )


class ModerationStatusView(APIView):
    def get(self, request):
        return Response(classifier_status())


class FeedbackView(generics.CreateAPIView):
    """Anonymous feedback: who sent it is not stored."""

    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
