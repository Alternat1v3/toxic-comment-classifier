from types import SimpleNamespace

from django.test import SimpleTestCase

from chat.moderation import classifier
from chat.moderation.classifier import BertClassifier, KeywordClassifier
from chat.moderation.labels import LABELS
from chat.moderation.pipeline import moderate

from .helpers import keyword_classifier


def fake_config(names):
    return SimpleNamespace(num_labels=len(names), id2label=dict(enumerate(names)))


class KeywordClassifierTests(SimpleTestCase):
    def test_clean_message_is_non_toxic(self):
        prediction = KeywordClassifier().predict("Want to study together?")
        self.assertEqual(prediction.label, "non-toxic")
        self.assertFalse(prediction.is_toxic)

    def test_uses_the_label_of_the_most_serious_word(self):
        prediction = KeywordClassifier().predict("you stupid idiot, I will kill you")
        self.assertEqual(prediction.label, "threat")
        self.assertEqual(prediction.source, "keywords")


class LabelMappingTests(SimpleTestCase):
    def test_old_models_with_generic_names_use_the_training_order(self):
        names = BertClassifier._labels_from_config(fake_config([f"LABEL_{i}" for i in range(7)]))
        self.assertEqual(names, LABELS)

    def test_models_that_saved_their_labels_keep_them(self):
        shuffled = list(reversed(LABELS))
        self.assertEqual(BertClassifier._labels_from_config(fake_config(shuffled)), shuffled)

    def test_rejects_a_model_with_the_wrong_number_of_outputs(self):
        with self.assertRaises(ValueError):
            BertClassifier._labels_from_config(fake_config(["LABEL_0", "LABEL_1"]))

    def test_rejects_unknown_labels(self):
        with self.assertRaises(ValueError):
            BertClassifier._labels_from_config(fake_config(LABELS[:-1] + ["spam"]))


class FallbackTests(SimpleTestCase):
    def test_falls_back_to_keywords_without_a_model(self):
        with keyword_classifier():
            self.assertIsInstance(classifier.get_classifier(), KeywordClassifier)
            self.assertEqual(classifier.classifier_status()["source"], "keywords")

    def test_moderate_classifies_the_original_and_filters_what_is_shown(self):
        with keyword_classifier():
            result = moderate("Shut up, idiot")
        self.assertEqual(result.prediction.label, "insult")
        self.assertEqual(result.shown, "Shut up, fool")
        self.assertTrue(result.was_filtered)
