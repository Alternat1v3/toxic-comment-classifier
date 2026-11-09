from django.urls import path

from . import views

urlpatterns = [
    path("auth/csrf/", views.CsrfView.as_view(), name="csrf"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/me/", views.MeView.as_view(), name="me"),
    path("users/", views.ContactListView.as_view(), name="contacts"),
    path("conversations/<str:username>/", views.ConversationView.as_view(), name="conversation"),
    path("moderation/check/", views.ModerationCheckView.as_view(), name="moderation-check"),
    path("moderation/status/", views.ModerationStatusView.as_view(), name="moderation-status"),
    path("feedback/", views.FeedbackView.as_view(), name="feedback"),
]
