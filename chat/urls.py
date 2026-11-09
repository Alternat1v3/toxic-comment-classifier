from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    RegisteredUsersAPIView,
    RegistrationAPIView,
    LoginAPIView,
    LogoutAPIView,
    CheckLoginStatus,
    MessageListView,
    PreprocessedMessagesAPIView,
    FeedbackView,
)

urlpatterns = [
    path(
        "registered-users/", RegisteredUsersAPIView.as_view(), name="registered-users"
    ),
    path("register", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path(
        "api/check_login_status/", CheckLoginStatus.as_view(), name="check_login_status"
    ),
    path(
        "api/messages/<str:username>/<str:contact_username>/",
        MessageListView.as_view(),
        name="message-list",
    ),
    path(
        "api/preprocessed_messages/",
        PreprocessedMessagesAPIView.as_view(),
        name="preprocessed-messages",
    ),
    path("api/feedback/", FeedbackView.as_view(), name="feedback"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from django.urls import path
# from .views import (
#     RegisteredUsersAPIView,
#     RegistrationAPIView,
#     LoginAPIView,
#     LogoutAPIView,
#     CheckLoginStatus,
# )

# urlpatterns = [
#     path(
#         "registered-users/", RegisteredUsersAPIView.as_view(), name="registered-users"
#     ),
#     path("register", RegistrationAPIView.as_view(), name="register"),
#     path("login/", LoginAPIView.as_view(), name="login"),
#     path("logout/", LogoutAPIView.as_view(), name="logout"),
#     path(
#         "api/check_login_status/", CheckLoginStatus.as_view(), name="check_login_status"
#     ),
# ]
