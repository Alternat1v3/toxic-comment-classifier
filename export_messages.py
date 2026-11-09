import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

import csv
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from chat.models import Message

csv_file = "chat_data_labeled.csv"
with open(csv_file, "w", newline="") as csvfile:
    fieldnames = ["sender", "receiver", "content", "timestamp", "label"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for message in Message.objects.all():
        writer.writerow(
            {
                "sender": message.sender.username,
                "receiver": message.receiver.username,
                "content": message.content,
                "timestamp": message.timestamp,
                "label": "non-toxic",
            }
        )

print("Successfully exported messages to chat_data_labeled.csv")

df = pd.read_csv(csv_file)

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

toxic_words_df = pd.read_csv("toxic_words.csv")
toxic_words_dict = {row["Word"]: row["Label"] for _, row in toxic_words_df.iterrows()}


def preprocess_text(text):
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.lower()
    text = " ".join(word for word in text.split() if word not in stop_words)
    text = " ".join(stemmer.stem(word) for word in text.split())
    return text


def get_toxic_label(text):
    words = set(text.split())
    for word in words:
        if word in toxic_words_dict:
            return toxic_words_dict[word]
    return "non-toxic"


if "content" in df.columns:
    df["preprocessed_content"] = df["content"].apply(preprocess_text)
    df["label"] = df["preprocessed_content"].apply(get_toxic_label)
    df.to_csv("preprocessed_chat_data.csv", index=False)
    print("Preprocessing completed and saved to preprocessed_chat_data.csv")
else:
    print("Error: 'content' column not found in the DataFrame")
