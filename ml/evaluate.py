"""
Score a trained model on any labelled CSV with `content` and `label` columns.

    python ml/evaluate.py ml/data/challenge.csv                 # the model in ml/model
    python ml/evaluate.py ml/data/challenge.csv --model path/to/model --save results/challenge.json
"""

import argparse
import csv
import json
import os
from pathlib import Path

import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

HERE = Path(__file__).resolve().parent
LABELS = ["identity hate", "insult", "threat", "obscene", "severe toxic", "toxic", "non-toxic"]


def model_labels(config):
    names = [config.id2label[i] for i in range(config.num_labels)]
    # Models saved before the labels were stored in the config only have LABEL_0, LABEL_1, ...
    return list(LABELS) if all(name.startswith("LABEL_") for name in names) else names


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data", type=Path)
    parser.add_argument("--model", type=Path, default=HERE / "model")
    parser.add_argument("--save", type=Path, help="Write the scores and every prediction to this JSON file.")
    parser.add_argument("--threads", type=int, default=os.cpu_count())
    args = parser.parse_args()

    torch.set_num_threads(args.threads)
    with open(args.data, newline="", encoding="utf-8") as f:
        rows = [(row["content"], row["label"]) for row in csv.DictReader(f)]
    texts = [text for text, _ in rows]
    truth = [label for _, label in rows]

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model).eval()
    names = model_labels(model.config)
    with torch.inference_mode():
        logits = model(**tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="pt")).logits
    predicted = [names[i] for i in logits.argmax(dim=-1).tolist()]

    accuracy = accuracy_score(truth, predicted)
    macro_f1 = f1_score(truth, predicted, labels=LABELS, average="macro", zero_division=0)
    print(f"{args.model.name} on {args.data.name}: accuracy {accuracy:.1%}, macro F1 {macro_f1:.3f} ({len(texts)} messages)")
    print(classification_report(truth, predicted, labels=LABELS, zero_division=0))

    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "model": args.model.name,
            "data": args.data.name,
            "accuracy": round(accuracy, 4),
            "macro_f1": round(macro_f1, 4),
            "confusion_matrix": {"labels": LABELS, "rows_are_true_labels": confusion_matrix(truth, predicted, labels=LABELS).tolist()},
            "predictions": [{"content": t, "label": y, "predicted": p} for t, y, p in zip(texts, truth, predicted)],
        }
        args.save.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
