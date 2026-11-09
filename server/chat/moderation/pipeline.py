"""What happens to every chat message before it is delivered."""

from dataclasses import dataclass

from .classifier import Prediction, classify
from .word_filter import filter_words


@dataclass(frozen=True)
class ModeratedMessage:
    original: str
    shown: str  # what the receiver sees
    prediction: Prediction

    @property
    def was_filtered(self):
        return self.shown != self.original


def moderate(text):
    """Classify the message as typed, then replace offensive words in what gets shown."""
    prediction = classify(text)
    return ModeratedMessage(original=text, shown=filter_words(text).text, prediction=prediction)
