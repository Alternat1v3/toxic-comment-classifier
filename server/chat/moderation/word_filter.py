"""
Replaces offensive words with milder ones before a message is shown.

Matching is whole-word and case-insensitive, with common endings ("idiots",
"fucking"), so words that merely contain a listed word ("skills", "Dickens")
are left alone.
"""

import csv
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

WORD_LIST = Path(__file__).resolve().parent / "data" / "word_list.csv"
ENDINGS = r"(?:s|es|ed|er|ers|ing|in)?"


@dataclass(frozen=True)
class Entry:
    word: str
    replacement: str
    label: str


@dataclass(frozen=True)
class FilterResult:
    text: str
    matches: tuple  # the Entry for each word that was replaced, in order


@lru_cache(maxsize=1)
def load_word_list(path=WORD_LIST):
    with open(path, newline="", encoding="utf-8") as f:
        entries = [Entry(row["word"].strip().lower(), row["replacement"].strip(), row["label"].strip()) for row in csv.DictReader(f)]
    # Longest words first, so a longer entry wins over one it contains.
    entries.sort(key=lambda e: len(e.word), reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(e.word) for e in entries) + r")" + ENDINGS + r"\b", re.IGNORECASE)
    return {e.word: e for e in entries}, pattern


def filter_words(text):
    """Return the text with listed words replaced, and which entries matched."""
    entries, pattern = load_word_list()
    matches = []

    def replace(match):
        entry = entries[match.group(1).lower()]
        matches.append(entry)
        replacement = entry.replacement
        # Keep a capital letter at the start of a sentence.
        if match.group(0)[0].isupper():
            replacement = replacement[0].upper() + replacement[1:]
        return replacement

    return FilterResult(pattern.sub(replace, text), tuple(matches))
