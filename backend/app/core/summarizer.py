import nltk
import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer

sp = spacy.load("en_core_web_sm")


def split(text):
    doc = sp(text)
    sents = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 15]
    return sents


def score(sents):
    vect = TfidfVectorizer(stop_words="english")
    X = vect.fit_transform(sents)
    scores = np.asarray(X.sum(axis=1)).ravel()
    return scores


def pos_bias(n):
    bias = []
    for i in range(n):
        pos = i / max(n - 1, 1)
        score = score = np.exp(-4 * (pos - 0.5) ** 2)
        bias.append(score)
    return np.array(bias)


def summarize(text, method="textrank", cnt=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))

    if method == "lsa":
        print("USING LSA")
        summarizer = LsaSummarizer()
    else:
        print("USING TRS")
        summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, cnt)
    # print("\n",summary)
    return [str(s) for s in summary]


def scene_summary(text, lines=3):
    sentences = split(text)
    if len(sentences) <= lines:
        return " ".join(sentences)

    tfidf = score(sentences)
    pos = pos_bias(len(sentences))

    fs = tfidf * 0.7 + pos * 0.3
    rid = np.argsort(fs)[::-1]

    chosen = sorted(rid[: lines * 2])
    chosen_sent = [sentences[i] for i in chosen]

    summary = summarize(text,cnt=lines)

    final = []
    for s in chosen_sent + summary:
        if s not in final:
            final.append(s)
    return " ".join(final[:lines])


def summarize_scenes(scenes, lines=3):
    for scene in scenes:
        scene.summary = scene_summary(scene.text, lines)
    return scenes


if __name__ == "__main__":
    nltk.download("punkt")
    nltk.download("punkt_tab")
