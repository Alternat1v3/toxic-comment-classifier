"""
Classifies a chat message into one of seven toxicity labels.

The main classifier is a BERT model fine-tuned on labelled chat messages (see ml/).
When the model files or the ML packages are missing, a keyword classifier based on
the word list takes over, so the app still runs without the 420 MB model.
"""

import logging
import os
import threading
from dataclasses import dataclass, field

from django.conf import settings

from .labels import LABELS, NON_TOXIC
from .word_filter import filter_words

log = logging.getLogger(__name__)

# How serious each label is, used when several listed words appear in one message.
SEVERITY = {label: rank for rank, label in enumerate(["toxic", "obscene", "insult", "severe toxic", "threat", "identity hate"])}


@dataclass(frozen=True)
class Prediction:
    label: str
    score: float  # confidence for `label`, 0 to 1
    source: str  # "bert" or "keywords"
    scores: dict = field(default_factory=dict)  # every label's probability (BERT only)

    @property
    def is_toxic(self):
        return self.label != NON_TOXIC


class KeywordClassifier:
    source = "keywords"

    def predict(self, text):
        matches = filter_words(text).matches
        if not matches:
            return Prediction(NON_TOXIC, 1.0, self.source)
        worst = max(matches, key=lambda entry: SEVERITY.get(entry.label, 0))
        return Prediction(worst.label, 1.0, self.source)


def softmax_is_reliable(torch, trials=20):
    """
    PyTorch 2.4.0 on Windows computed softmax wrongly when it used more than one CPU thread
    (wrong in about 4 of 5 runs on a 4-core i3). Attention then returned NaN, and every
    message came out as "identity hate". This compares float32 softmax with float64.
    """
    x = torch.randn(4, 12, 32, 32)
    expected = torch.softmax(x.double(), dim=-1)
    return all((torch.softmax(x, dim=-1).double() - expected).abs().max().item() < 1e-4 for _ in range(trials))


class BertClassifier:
    source = "bert"

    def __init__(self, model_dir, threads=None, max_length=128):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        torch.set_num_threads(threads or os.cpu_count() or 1)
        if not softmax_is_reliable(torch):
            raise RuntimeError(f"PyTorch {torch.__version__} computes softmax wrongly on this machine; install torch>=2.5.1.")
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.eval()
        self.labels = self._labels_from_config(self.model.config)

    @staticmethod
    def _labels_from_config(config):
        names = [config.id2label[i] for i in range(config.num_labels)]
        # Models trained before labels were saved in the config only have LABEL_0, LABEL_1, ...
        if all(name.startswith("LABEL_") for name in names):
            if len(names) != len(LABELS):
                raise ValueError(f"Model has {len(names)} outputs, expected {len(LABELS)}")
            return list(LABELS)
        unknown = set(names) - set(LABELS)
        if unknown:
            raise ValueError(f"Model has unknown labels: {sorted(unknown)}")
        return names

    def predict(self, text):
        return self.predict_batch([text])[0]

    def predict_batch(self, texts):
        encoded = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=self.max_length)
        with self.torch.inference_mode():
            probs = self.model(**encoded).logits.softmax(dim=-1)
        predictions = []
        for row in probs.tolist():
            best = max(range(len(row)), key=row.__getitem__)
            predictions.append(
                Prediction(
                    label=self.labels[best],
                    score=round(row[best], 4),
                    source=self.source,
                    scores={label: round(p, 4) for label, p in zip(self.labels, row)},
                )
            )
        return predictions


_classifier = None
_lock = threading.Lock()


def _load():
    model_dir = settings.TOXICITY_MODEL_DIR
    if not (model_dir / "config.json").exists():
        log.warning("No model in %s; checking messages with the keyword list instead.", model_dir)
        return KeywordClassifier()
    try:
        classifier = BertClassifier(model_dir, threads=settings.TORCH_THREADS)
    except ImportError:
        log.warning("PyTorch/Transformers are not installed (pip install -r requirements-ml.txt); using the keyword list.")
        return KeywordClassifier()
    except RuntimeError as error:
        log.error("Cannot use the BERT model: %s Using the keyword list instead.", error)
        return KeywordClassifier()
    log.info("Loaded the BERT toxicity model from %s", model_dir)
    return classifier


def get_classifier():
    global _classifier
    if _classifier is None:
        with _lock:
            if _classifier is None:
                _classifier = _load()
    return _classifier


def classify(text):
    return get_classifier().predict(text)


def classifier_status():
    classifier = get_classifier()
    return {"source": classifier.source, "labels": LABELS}
