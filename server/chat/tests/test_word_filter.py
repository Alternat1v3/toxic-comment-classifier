from django.test import SimpleTestCase

from chat.moderation.word_filter import filter_words


class WordFilterTests(SimpleTestCase):
    def test_replaces_listed_words(self):
        result = filter_words("you are an idiot")
        self.assertEqual(result.text, "you are an fool")
        self.assertEqual([entry.word for entry in result.matches], ["idiot"])

    def test_is_case_insensitive_and_keeps_a_leading_capital(self):
        self.assertEqual(filter_words("Idiot.").text, "Fool.")
        self.assertEqual(filter_words("IDIOT").text, "Fool")

    def test_catches_common_endings(self):
        self.assertEqual(filter_words("idiots everywhere").text, "fool everywhere")
        self.assertEqual(filter_words("so fucking slow").text, "so f-word slow")

    def test_leaves_words_that_only_contain_a_listed_word(self):
        # The original substring matching turned "skills" into "shurts".
        for text in ["great skills", "Scunthorpe", "Charles Dickens", "passport", "skilled"]:
            with self.subTest(text=text):
                result = filter_words(text)
                self.assertEqual(result.text, text)
                self.assertEqual(result.matches, ())

    def test_clean_text_is_unchanged(self):
        self.assertEqual(filter_words("See you at 5 in the library?").text, "See you at 5 in the library?")
