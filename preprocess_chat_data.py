# import pandas as pd
# import re
# import nltk
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer

# df = pd.read_csv("chat_data_labeled.csv")

# print("Columns in the DataFrame:", df.columns)

# nltk.download("stopwords")
# stop_words = set(stopwords.words("english"))
# stemmer = PorterStemmer()

# toxic_words_df = pd.read_csv("toxic_words.csv")
# toxic_words = set(toxic_words_df["Word"])


# def preprocess_text(text):

#     text = re.sub(r"<.*?>", "", text)
#     text = re.sub(r"[^\w\s]", "", text)
#     text = re.sub(r"\d+", "", text)
#     text = text.lower()
#     text = " ".join(word for word in text.split() if word not in stop_words)
#     text = " ".join(stemmer.stem(word) for word in text.split())
#     return text


# def is_toxic(text):
#     words = set(text.split())
#     return any(word in toxic_words for word in words)


# def update_label(is_toxic):
#     return "toxic" if is_toxic else "non-toxic"


# if "content" in df.columns:
#     df["preprocessed_content"] = df["content"].apply(preprocess_text)
#     df["is_toxic"] = df["preprocessed_content"].apply(is_toxic)
#     df["label"] = df["is_toxic"].apply(update_label)
#     df.to_csv("preprocessed_chat_data.csv", index=False)
#     print("Preprocessing completed and saved to preprocessed_chat_data.csv")
# else:
#     print("Error: 'content' column not found in the DataFrame")
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

df = pd.read_csv("chat_data.csv")

print("Columns in the DataFrame:", df.columns)

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

toxic_words_df = pd.read_csv("toxic_words.csv")
toxic_words = {row["Word"]: row["Label"] for _, row in toxic_words_df.iterrows()}


def preprocess_text(text):

    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.lower()
    text = " ".join(word for word in text.split() if word not in stop_words)
    text = " ".join(stemmer.stem(word) for word in text.split())
    return text


def get_toxic_labels(text):
    words = set(text.split())
    labels = {toxic_words[word] for word in words if word in toxic_words}
    return labels


def update_label(labels):
    return ", ".join(labels) if labels else "non-toxic"


if "content" in df.columns:
    df["preprocessed_content"] = df["content"].apply(preprocess_text)
    df["labels"] = df["preprocessed_content"].apply(get_toxic_labels)
    df["label"] = df["labels"].apply(update_label)

    df.drop(columns=["labels"], inplace=True)

    df.to_csv("preprocessed_chat_data.csv", index=False)
    print("Preprocessing completed and saved to preprocessed_chat_data.csv")
else:
    print("Error: 'content' column not found in the DataFrame")
