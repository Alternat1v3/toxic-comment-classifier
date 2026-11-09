import json
import csv
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, CustomUser
from django.db import models
from .bert_model import predict_toxicity


class ChatConsumer(AsyncWebsocketConsumer):
    @staticmethod
    def load_synonyms_from_csv(file_path):
        synonyms = {}
        try:
            with open(file_path, mode="r") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    word = row[0]
                    synonyms[word] = row[1].split(", ")
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
        return synonyms

    word_synonyms = load_synonyms_from_csv("chat/toxic_word_synonyms.csv")

    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.other_user_username = self.scope["url_route"]["kwargs"][
            "other_user_username"
        ]

        self.room_name = f"chat_{min(self.username, self.other_user_username)}_{max(self.username, self.other_user_username)}"
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_previous_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json["message"]
        sender = text_data_json["sender"]
        timestamp = text_data_json.get("timestamp", None)

        toxicity_label = await database_sync_to_async(predict_toxicity)(content)

        filtered_content = self.replace_offensive_words(content)

        message_details = await self.save_message(
            sender, self.other_user_username, filtered_content, toxicity_label
        )

        if toxicity_label != "non-toxic":
            await self.increment_toxic_count(sender, message_details["message_obj"])

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": filtered_content,
                "sender": sender,
                "timestamp": message_details["timestamp"],
                "toxicity_label": toxicity_label,
            },
        )

    async def chat_message(self, event):
        content = event["message"]
        sender = event["sender"]
        timestamp = event["timestamp"]
        toxicity_label = event.get("toxicity_label", "non-toxic")

        await self.send(
            text_data=json.dumps(
                {
                    "message": content,
                    "sender": sender,
                    "timestamp": timestamp,
                    "toxicity_label": toxicity_label,
                }
            )
        )

    @database_sync_to_async
    def save_message(self, sender, receiver, content, toxicity_label):
        sender_user = CustomUser.objects.get(username=sender)
        receiver_user = CustomUser.objects.get(username=receiver)
        message = Message.objects.create(
            sender=sender_user,
            receiver=receiver_user,
            content=content,
            toxicity_label=toxicity_label,
        )
        return {
            "content": message.content,
            "sender": message.sender.username,
            "timestamp": message.timestamp.strftime("%H:%M"),
            "message_obj": message,
        }

    @database_sync_to_async
    def increment_toxic_count(self, username, message):
        user = CustomUser.objects.get(username=username)
        user.increment_toxic_count(1, message)

    @database_sync_to_async
    def get_previous_messages(self):
        messages = Message.objects.filter(
            models.Q(
                sender__username=self.username,
                receiver__username=self.other_user_username,
            )
            | models.Q(
                sender__username=self.other_user_username,
                receiver__username=self.username,
            )
        ).order_by("timestamp")

        return [
            {
                "content": msg.content,
                "sender": msg.sender.username,
                "timestamp": msg.timestamp.strftime("%H:%M"),
            }
            for msg in messages
        ]

    async def send_previous_messages(self):
        messages = await self.get_previous_messages()
        for msg in messages:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": msg["content"],
                        "sender": msg["sender"],
                        "timestamp": msg["timestamp"],
                    }
                )
            )

    def replace_offensive_words(self, content):
        for word, synonyms in self.word_synonyms.items():
            for synonym in synonyms:
                content = content.replace(word, synonym)
        return content
