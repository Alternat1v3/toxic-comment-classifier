from django.contrib.auth import get_user_model
from django.test import TestCase

from chat.admin_site import label_kind
from chat.models import Feedback, Message

User = get_user_model()


class AdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("moderator", "moderator@example.com", "a-long-test-password")
        self.ayesha = User.objects.create_user("ayesha", "ayesha@example.com", "a-long-test-password")
        self.bilal = User.objects.create_user("bilal", "bilal@example.com", "a-long-test-password", toxic_message_count=1)
        Message.objects.create(sender=self.ayesha, receiver=self.bilal, content="hi", toxicity_label="non-toxic", toxicity_score=0.9)
        Message.objects.create(
            sender=self.bilal, receiver=self.ayesha, content="you fool", original_content="you idiot", toxicity_label="insult", toxicity_score=0.8
        )
        Feedback.objects.create(feedback="Nice app")
        self.client.force_login(self.admin)

    def test_dashboard_shows_moderation_numbers(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        stats = response.context["stats"]
        self.assertEqual((stats["messages"], stats["flagged"], stats["flagged_pct"], stats["feedback"]), (2, 1, 50, 1))
        self.assertEqual([u.username for u in stats["top_users"]], ["bilal"])
        self.assertContains(response, "you idiot")  # moderators see what was really typed
        self.assertContains(response, "SafeChat")

    def test_lists_show_label_badges(self):
        response = self.client.get("/admin/chat/message/?flagged=yes")
        self.assertContains(response, '<span class="sc-badge sc-badge--warn">insult · 80%</span>', html=True)
        self.assertNotContains(response, ">hi<")

    def test_every_admin_page_renders(self):
        for url in ["/admin/chat/user/", f"/admin/chat/user/{self.bilal.pk}/change/", "/admin/chat/message/", "/admin/chat/feedback/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_label_colours_match_the_chat_app(self):
        self.assertEqual(label_kind("non-toxic"), "ok")
        self.assertEqual(label_kind("insult"), "warn")
        self.assertEqual(label_kind("threat"), "severe")
