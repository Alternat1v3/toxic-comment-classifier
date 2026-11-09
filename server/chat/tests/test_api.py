from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase

from chat.models import Feedback, Message

from .helpers import keyword_classifier

User = get_user_model()
PASSWORD = "a-long-test-password"


class ApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()  # rate limits are kept in the cache
        self.ayesha = User.objects.create_user("ayesha", "ayesha@example.com", PASSWORD)
        self.bilal = User.objects.create_user("bilal", "bilal@example.com", PASSWORD)
        self.sara = User.objects.create_user("sara", "sara@example.com", PASSWORD)


class AuthTests(ApiTestCase):
    def test_register_creates_the_user_and_signs_them_in(self):
        response = self.client.post(
            "/api/auth/register/", {"username": "omar", "email": "omar@example.com", "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "omar")
        self.assertNotIn("password", response.data)
        self.assertEqual(self.client.get("/api/auth/me/").data["username"], "omar")

    def test_register_rejects_weak_passwords(self):
        response = self.client.post(
            "/api/auth/register/", {"username": "omar", "email": "omar@example.com", "password": "12345"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", str(response.data).lower())

    def test_register_rejects_a_taken_email(self):
        response = self.client.post(
            "/api/auth/register/", {"username": "omar", "email": "ayesha@example.com", "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_login_and_logout(self):
        response = self.client.post("/api/auth/login/", {"username": "ayesha", "password": PASSWORD}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "ayesha")
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, 204)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 403)

    def test_login_with_a_wrong_password_fails(self):
        response = self.client.post("/api/auth/login/", {"username": "ayesha", "password": "wrong"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_csrf_endpoint_sets_the_cookie(self):
        response = self.client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, 204)
        self.assertIn("csrftoken", response.cookies)

    def test_sign_in_needs_the_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        credentials = {"username": "ayesha", "password": PASSWORD}
        self.assertEqual(client.post("/api/auth/login/", credentials, format="json").status_code, 403)

        token = client.get("/api/auth/csrf/").cookies["csrftoken"].value
        response = client.post("/api/auth/login/", credentials, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)

    def test_sign_up_needs_the_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        data = {"username": "omar", "email": "omar@example.com", "password": PASSWORD}
        self.assertEqual(client.post("/api/auth/register/", data, format="json").status_code, 403)
        self.assertFalse(User.objects.filter(username="omar").exists())


class PrivacyTests(ApiTestCase):
    def test_signed_out_visitors_get_nothing(self):
        for url in ["/api/auth/me/", "/api/users/", "/api/conversations/bilal/", "/api/moderation/status/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_contacts_exclude_yourself_and_hide_emails(self):
        self.client.force_authenticate(self.ayesha)
        users = self.client.get("/api/users/").data
        self.assertEqual([u["username"] for u in users], ["bilal", "sara"])
        self.assertTrue(all("email" not in u for u in users))

    def test_you_only_see_your_own_conversations(self):
        Message.objects.create(sender=self.ayesha, receiver=self.bilal, content="hi bilal")
        Message.objects.create(sender=self.bilal, receiver=self.ayesha, content="hi ayesha")
        Message.objects.create(sender=self.bilal, receiver=self.sara, content="a secret for sara")

        self.client.force_authenticate(self.ayesha)
        messages = self.client.get("/api/conversations/bilal/").data
        self.assertEqual([m["message"] for m in messages], ["hi bilal", "hi ayesha"])
        # Asking for "sara" only returns messages between ayesha and sara (none), not bilal's.
        self.assertEqual(self.client.get("/api/conversations/sara/").data, [])

    def test_unknown_user_is_404(self):
        self.client.force_authenticate(self.ayesha)
        self.assertEqual(self.client.get("/api/conversations/nobody/").status_code, 404)


class ModerationApiTests(ApiTestCase):
    def test_check_returns_the_label_and_the_filtered_text(self):
        self.client.force_authenticate(self.ayesha)
        with keyword_classifier():
            response = self.client.post("/api/moderation/check/", {"text": "you idiot"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["label"], "insult")
        self.assertTrue(response.data["is_toxic"])
        self.assertEqual(response.data["shown_as"], "you fool")
        self.assertEqual(response.data["source"], "keywords")
        self.assertFalse(Message.objects.exists())  # checking text never sends it

    def test_check_rejects_empty_text(self):
        self.client.force_authenticate(self.ayesha)
        self.assertEqual(self.client.post("/api/moderation/check/", {"text": "  "}, format="json").status_code, 400)


class FeedbackTests(ApiTestCase):
    def test_feedback_is_stored_without_the_sender(self):
        self.client.force_authenticate(self.ayesha)
        response = self.client.post("/api/feedback/", {"feedback": "Love the dark mode"}, format="json")
        self.assertEqual(response.status_code, 201)
        feedback = Feedback.objects.get()
        self.assertEqual(feedback.feedback, "Love the dark mode")
        self.assertFalse(hasattr(feedback, "user"))
