"""
Fine-tune BERT to label chat messages with one of seven toxicity classes.

    python ml/train.py                      # data/train.csv -> model/, results/
    python ml/train.py --epochs 10 --seed 7

The data is split 80/20, stratified by label, with a fixed seed. The model never sees
the test rows during training; they are only used for the scores in results/metrics.json.
"""

import argparse
import csv
import json
import math
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

HERE = Path(__file__).resolve().parent

# Same order as server/chat/moderation/labels.py. The names are also saved in the model's config.
LABELS = ["identity hate", "insult", "threat", "obscene", "severe toxic", "toxic", "non-toxic"]


def read_dataset(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [(row["content"].strip(), row["label"].strip()) for row in csv.DictReader(f)]
    unknown = {label for _, label in rows} - set(LABELS)
    if unknown:
        raise SystemExit(f"Unknown labels in {path}: {sorted(unknown)}")
    return [text for text, _ in rows], [LABELS.index(label) for _, label in rows]


def check_softmax(trials=20):
    """PyTorch 2.4.0 on Windows computed softmax wrongly with several CPU threads, so training learned nothing."""
    x = torch.randn(4, 12, 32, 32)
    expected = torch.softmax(x.double(), dim=-1)
    if any((torch.softmax(x, dim=-1).double() - expected).abs().max().item() > 1e-4 for _ in range(trials)):
        raise SystemExit(f"PyTorch {torch.__version__} computes softmax wrongly on this machine. Install torch>=2.5.1.")


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def predict(model, tokenizer, texts, batch_size=32, max_length=128):
    model.eval()
    predictions = []
    with torch.inference_mode():
        for start in range(0, len(texts), batch_size):
            batch = tokenizer(list(texts[start : start + batch_size]), padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            predictions += model(**batch).logits.argmax(dim=-1).tolist()
    return predictions


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, default=HERE / "data" / "train.csv")
    parser.add_argument("--base-model", default="bert-base-uncased")
    parser.add_argument("--out", type=Path, default=HERE / "model")
    parser.add_argument("--results", type=Path, default=HERE / "results")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--threads", type=int, default=os.cpu_count())
    args = parser.parse_args()

    set_seed(args.seed)
    torch.set_num_threads(args.threads)
    check_softmax()

    texts, labels = read_dataset(args.data)
    train_x, test_x, train_y, test_y = train_test_split(texts, labels, test_size=args.test_size, stratify=labels, random_state=args.seed)
    print(f"{len(texts)} examples: {len(train_x)} for training, {len(test_x)} held out for testing")

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=len(LABELS),
        id2label=dict(enumerate(LABELS)),
        label2id={label: i for i, label in enumerate(LABELS)},
    )

    steps_per_epoch = math.ceil(len(train_x) / args.batch_size)
    total_steps = steps_per_epoch * args.epochs
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps)

    started = time.time()
    order = list(range(len(train_x)))
    for epoch in range(1, args.epochs + 1):
        model.train()
        random.shuffle(order)
        epoch_loss = 0.0
        for start in range(0, len(order), args.batch_size):
            idx = order[start : start + args.batch_size]
            batch = tokenizer([train_x[i] for i in idx], padding=True, truncation=True, max_length=128, return_tensors="pt")
            loss = model(**batch, labels=torch.tensor([train_y[i] for i in idx])).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            epoch_loss += loss.item() * len(idx)
        print(f"epoch {epoch:>2}/{args.epochs}  loss {epoch_loss / len(order):.4f}  ({time.time() - started:.0f}s)")

    args.out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    print(f"Saved the model to {args.out}")

    predictions = predict(model, tokenizer, test_x)
    report = classification_report(test_y, predictions, labels=range(len(LABELS)), target_names=LABELS, output_dict=True, zero_division=0)
    metrics = {
        "accuracy": round(accuracy_score(test_y, predictions), 4),
        "macro_f1": round(f1_score(test_y, predictions, average="macro"), 4),
        "per_label": {label: {k: round(v, 4) for k, v in report[label].items()} for label in LABELS},
        "confusion_matrix": {"labels": LABELS, "rows_are_true_labels": confusion_matrix(test_y, predictions, labels=range(len(LABELS))).tolist()},
        "setup": {
            "base_model": args.base_model,
            "examples": len(texts),
            "train_examples": len(train_x),
            "test_examples": len(test_x),
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "seed": args.seed,
            "training_seconds": round(time.time() - started),
        },
    }
    args.results.mkdir(parents=True, exist_ok=True)
    (args.results / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    with open(args.results / "test_predictions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["content", "label", "predicted"])
        writer.writerows((text, LABELS[true], LABELS[pred]) for text, true, pred in zip(test_x, test_y, predictions))

    print(f"Test accuracy {metrics['accuracy']:.1%}, macro F1 {metrics['macro_f1']:.3f} on {len(test_x)} held-out examples")
    print(classification_report(test_y, predictions, labels=range(len(LABELS)), target_names=LABELS, zero_division=0))


if __name__ == "__main__":
    main()
