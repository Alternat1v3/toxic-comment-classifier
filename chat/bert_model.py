# from transformers import BertTokenizer, BertForSequenceClassification
# import torch

# model_path = "./results/checkpoint-9"

# tokenizer = BertTokenizer.from_pretrained(model_path)
# model = BertForSequenceClassification.from_pretrained(model_path)

# label_names = [
#     "identity hate",
#     "insult",
#     "threat",
#     "obscene",
#     "severe toxic",
#     "toxic",
#     "non-toxic",
# ]


# def predict_toxicity(text):

#     inputs = tokenizer(
#         text, return_tensors="pt", padding=True, truncation=True, max_length=128
#     )


#     outputs = model(**inputs)

#     # Get the label with the highest score
#     logits = outputs.logits
#     predicted_label = torch.argmax(logits, dim=1).item()

#     return label_names[predicted_label]


from transformers import BertTokenizer, BertForSequenceClassification
import torch

model_path = "./results/final_model"

tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

label_names = [
    "identity hate",
    "insult",
    "threat",
    "obscene",
    "severe toxic",
    "toxic",
    "non-toxic",
]


def predict_toxicity(text):
    inputs = tokenizer(
        text, return_tensors="pt", padding=True, truncation=True, max_length=128
    )
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_label = torch.argmax(logits, dim=1).item()
    return label_names[predicted_label]


# # Example Usage
# text = "fuck you"
# predicted_label = predict_toxicity(text)
# print(f"The predicted label for '{text}' is: {predicted_label}")
