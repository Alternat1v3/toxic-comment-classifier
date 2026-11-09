import pandas as pd


def load_toxic_synonyms():
    df = pd.read_csv("chat/toxic_word_synonyms.csv")
    toxic_synonyms = {}
    for _, row in df.iterrows():
        toxic_synonyms[row["Word"]] = row["Synonyms"]
    return toxic_synonyms


toxic_synonyms = load_toxic_synonyms()


def replace_toxic_words(text):
    words = text.split()
    for i, word in enumerate(words):
        if word in toxic_synonyms:
            words[i] = toxic_synonyms[word]
    return " ".join(words)
