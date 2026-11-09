import pandas as pd
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from sklearn.model_selection import train_test_split
import torch

df = pd.read_csv("./train_berttt.csv", encoding="ISO-8859-1")


tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


labels = {
    "identity hate": 0,
    "insult": 1,
    "threat": 2,
    "obscene": 3,
    "severe toxic": 4,
    "toxic": 5,
    "non-toxic": 6,
}


def tokenize_function(text):
    return tokenizer(text, padding="max_length", truncation=True)


df["labels"] = df["label"].apply(lambda x: labels[x])


df["labels"] = df["labels"].fillna(labels["non-toxic"])

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["content"].tolist(), df["labels"].tolist(), test_size=0.2
)


train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)


class ToxicityDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_dataset = ToxicityDataset(train_encodings, train_labels)
val_dataset = ToxicityDataset(val_encodings, val_labels)

model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=7)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=25,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    evaluation_strategy="steps",
    save_strategy="steps",
    save_steps=500,
    load_best_model_at_end=True,
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()


model_save_path = "./results/checkpoint-9"
trainer.save_model(model_save_path)
tokenizer.save_pretrained(model_save_path)

# import pandas as pd
# from transformers import (
#     BertTokenizer,
#     BertForSequenceClassification,
#     Trainer,
#     TrainingArguments,
#     get_scheduler,
# )
# from sklearn.model_selection import train_test_split
# import torch
# from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# df = pd.read_csv("./train_berttt.csv", encoding="ISO-8859-1")

# tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# labels = {
#     "identity hate": 0,
#     "insult": 1,
#     "threat": 2,
#     "obscene": 3,
#     "severe toxic": 4,
#     "toxic": 5,
#     "non-toxic": 6,
# }

# max_length = 128


# def tokenize_function(texts):
#     return tokenizer(
#         texts, padding="max_length", truncation=True, max_length=max_length
#     )


# df["labels"] = df["label"].apply(lambda x: labels.get(x, labels["non-toxic"]))

# train_texts, val_texts, train_labels, val_labels = train_test_split(
#     df["content"].tolist(), df["labels"].tolist(), test_size=0.2
# )

# train_encodings = tokenize_function(train_texts)
# val_encodings = tokenize_function(val_texts)


# class ToxicityDataset(torch.utils.data.Dataset):
#     def __init__(self, encodings, labels):
#         self.encodings = encodings
#         self.labels = labels

#     def __getitem__(self, idx):
#         item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
#         item["labels"] = torch.tensor(self.labels[idx])
#         return item

#     def __len__(self):
#         return len(self.labels)


# train_dataset = ToxicityDataset(train_encodings, train_labels)
# val_dataset = ToxicityDataset(val_encodings, val_labels)

# model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=7)

# training_args = TrainingArguments(
#     output_dir="./results",
#     num_train_epochs=25,
#     per_device_train_batch_size=16,
#     per_device_eval_batch_size=32,
#     warmup_steps=100,
#     weight_decay=0.01,
#     logging_dir="./logs",
#     logging_steps=10,
#     evaluation_strategy="steps",
#     save_strategy="steps",
#     save_steps=500,
#     load_best_model_at_end=True,
#     fp16=True,  # Mixed precision
#     gradient_accumulation_steps=2,  # Adjust based on your GPU memory
# )


# def compute_metrics(p):
#     preds = p.predictions.argmax(-1)
#     labels = p.label_ids
#     accuracy = accuracy_score(labels, preds)
#     precision, recall, f1, _ = precision_recall_fscore_support(
#         labels, preds, average="weighted"
#     )
#     return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=val_dataset,
#     compute_metrics=compute_metrics,
# )

# trainer.train()

# model_save_path = "./results/checkpoint-9"
# trainer.save_model(model_save_path)
# tokenizer.save_pretrained(model_save_path)
