from asgiref.sync import sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TransactionTestCase, override_settings

from chat.models import Message
from chat.routing import websocket_urlpatterns

from .helpers import keyword_classifier

User = get_user_model()
application = URLRouter(websocket_urlpatterns)


@override_settings(CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}})
class ChatConsumerTests(TransactionTestCase):
    def setUp(self):
        self.ayesha = User.objects.create_user("ayesha", "ayesha@example.com", "a-long-test-password")
        self.bilal = User.objects.create_user("bilal", "bilal@example.com", "a-long-test-password")

    def socket(self, user, other):
        communicator = WebsocketCommunicator(application, f"/ws/chat/{other}/")
        communicator.scope["user"] = user
        return communicator

    async def test_signed_out_users_are_turned_away(self):
        communicator = self.socket(AnonymousUser(), "bilal")
        connected, code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(code, 4401)

    async def test_unknown_contact_is_turned_away(self):
        communicator = self.socket(self.ayesha, "nobody")
        connected, code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(code, 4404)

    async def test_history_then_live_messages(self):
        await sync_to_async(Message.objects.create)(sender=self.bilal, receiver=self.ayesha, content="earlier message")
        with keyword_classifier():
            ayesha = self.socket(self.ayesha, "bilal")
            bilal = self.socket(self.bilal, "ayesha")
            self.assertTrue((await ayesha.connect())[0])
            self.assertTrue((await bilal.connect())[0])

            history = await ayesha.receive_json_from()
            self.assertEqual(history["type"], "history")
            self.assertEqual([m["message"] for m in history["messages"]], ["earlier message"])
            await bilal.receive_json_from()  # bilal's own history

            await ayesha.send_json_to({"message": "Hey, want to study?", "sender": "bilal"})
            for socket in (ayesha, bilal):
                event = await socket.receive_json_from()
                self.assertEqual(event["type"], "message")
                # The sender always comes from the session, never from the client.
                self.assertEqual(event["message"]["sender"], "ayesha")
                self.assertEqual(event["message"]["toxicity_label"], "non-toxic")

            await ayesha.disconnect()
            await bilal.disconnect()

    async def test_toxic_messages_are_filtered_flagged_and_counted(self):
        with keyword_classifier():
            ayesha = self.socket(self.ayesha, "bilal")
            await ayesha.connect()
            await ayesha.receive_json_from()  # history

            await ayesha.send_json_to({"message": "you idiot"})
            event = await ayesha.receive_json_from()
            await ayesha.disconnect()

        self.assertEqual(event["message"]["message"], "you fool")
        self.assertEqual(event["message"]["toxicity_label"], "insult")
        message = await sync_to_async(Message.objects.get)()
        self.assertEqual(message.original_content, "you idiot")
        await sync_to_async(self.ayesha.refresh_from_db)()
        self.assertEqual(self.ayesha.toxic_message_count, 1)

    async def test_overlong_messages_are_rejected(self):
        with keyword_classifier():
            ayesha = self.socket(self.ayesha, "bilal")
            await ayesha.connect()
            await ayesha.receive_json_from()
            await ayesha.send_json_to({"message": "a" * 1001})
            event = await ayesha.receive_json_from()
            await ayesha.disconnect()
        self.assertEqual(event["type"], "error")
        self.assertEqual(await sync_to_async(Message.objects.count)(), 0)
