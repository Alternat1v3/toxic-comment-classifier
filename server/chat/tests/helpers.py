from contextlib import contextmanager
from pathlib import Path

from django.test import override_settings

from chat.moderation import classifier


@contextmanager
def keyword_classifier():
    """Run with the keyword classifier, so tests don't need the 420 MB model or PyTorch."""
    with override_settings(TOXICITY_MODEL_DIR=Path("does-not-exist")):
        classifier._classifier = None
        try:
            yield
        finally:
            classifier._classifier = None
