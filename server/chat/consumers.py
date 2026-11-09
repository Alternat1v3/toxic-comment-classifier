"""
Real-time chat. Every message is classified and filtered before it is stored and delivered.

Protocol (JSON over WebSocket):
  client -> server  {"message": "text"}
  server -> client  {"type": "history", "messages": [...]}      once, after connecting
                    {"type": "message", "message": {...}}       for every new message
                    {"type": "error", "detail": "..."}
"""

import json
import logging

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F, Q

from .models import Message
from .moderation.pipeline import moderate
from .serializers import MessageSerializer

log = logging.getLogger(__name__)
User = get_user_model()
HISTORY_LIMIT = 100

# Close codes in the 4000 range are for the app's own reasons.
NOT_SIGNED_IN = 4401
NO_SUCH_USER = 4404


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=NOT_SIGNED_IN)
            return

        self.other = await self.get_user(self.scope["url_route"]["kwargs"]["username"])
        if self.other is None or self.other.pk == self.user.pk:
            await self.close(code=NO_SUCH_USER)
            return

        first, second = sorted([self.user.pk, self.other.pk])
        self.group = f"chat_{first}_{second}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self.send_json({"type": "history", "messages": await self.get_history()})

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text = str(json.loads(text_data or "{}").get("message", "")).strip()
        except (json.JSONDecodeError, AttributeError):
            await self.send_json({"type": "error", "detail": "Messages must be JSON like {\"message\": \"hi\"}."})
            return
        if not text:
            return
        if len(text) > settings.MESSAGE_MAX_LENGTH:
            await self.send_json({"type": "error", "detail": f"Messages can be at most {settings.MESSAGE_MAX_LENGTH} characters."})
            return

        # The model runs in a worker thread so the event loop keeps serving other sockets.
        result = await sync_to_async(moderate, thread_sensitive=False)(text)
        payload = await self.save_message(result)
        await self.channel_layer.group_send(self.group, {"type": "chat.message", "message": payload})

    async def chat_message(self, event):
        await self.send_json({"type": "message", "message": event["message"]})

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.filter(username=username, is_active=True).first()

    @database_sync_to_async
    def get_history(self):
        messages = (
            Message.objects.filter(Q(sender=self.user, receiver=self.other) | Q(sender=self.other, receiver=self.user))
            .select_related("sender")
            .order_by("-timestamp", "-id")[:HISTORY_LIMIT]
        )
        return MessageSerializer(list(messages)[::-1], many=True).data

    @database_sync_to_async
    def save_message(self, result):
        prediction = result.prediction
        message = Message.objects.create(
            sender=self.user,
            receiver=self.other,
            content=result.shown,
            original_content=result.original,
            toxicity_label=prediction.label,
            toxicity_score=prediction.score,
            classifier=prediction.source,
        )
        if prediction.is_toxic:
            User.objects.filter(pk=self.user.pk).update(toxic_message_count=F("toxic_message_count") + 1)
        return MessageSerializer(message).data
