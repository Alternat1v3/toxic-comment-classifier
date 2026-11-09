import os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from chat.models import Message


def extract_chat_data():
    messages = Message.objects.all()
    chat_data = []

    for message in messages:
        chat_data.append(
            {
                "sender": message.sender.username,
                "receiver": message.receiver.username,
                "content": message.content,
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "BERT_toxicity_prediction": message.toxicity_label,
            }
        )

    keys = chat_data[0].keys() if chat_data else []

    with open("chat_data.csv", "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(chat_data)


if __name__ == "__main__":
    extract_chat_data()
    print("Chat data extracted to chat_data_labeled.csv")
