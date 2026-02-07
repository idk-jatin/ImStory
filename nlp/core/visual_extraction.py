from collections import Counter
from core.constants import (
    LIGHTING_TOKENS,
    WEATHER_TOKENS,
    MATERIAL_TOKENS,
    CONDITION_TOKENS,
)


class VisualEvidenceExtractor:

    def __init__(self):
        pass

    def extract(self, doc):
        evidence = {"lighting": [], "weather": [], "materials": [], "conditions": []}

        def is_negated(token):
            if any(c.dep_ == "neg" for c in token.children):
                return True
            if (
                any(c.dep_ == "neg" for c in token.head.children)
                and token.head.pos_ == "VERB"
            ):
                return True
            return False

        def expand_phrase(token):
            if token.i > 0:
                prev = token.nbor(-1)
                if prev.dep_ in {"amod", "compound"} and prev.head == token:
                    return f"{prev.text} {token.text}".lower()
            return token.text.lower()

        seen_tokens = set()

        for chunk in doc.noun_chunks:
            tokens = [t for t in chunk]
            lemmas = {t.lemma_.lower() for t in tokens}

            has_mat = any(l in MATERIAL_TOKENS for l in lemmas)
            has_cond = any(l in CONDITION_TOKENS for l in lemmas)

            if has_mat or has_cond:
                if is_negated(chunk.root):
                    continue

                clean_text = " ".join(
                    [t.text for t in tokens if t.pos_ not in {"DET", "PRON", "CC"}]
                )
                if not clean_text:
                    continue

                clean_text = clean_text.lower()

                if has_mat:
                    evidence["materials"].append(clean_text)
                if has_cond:
                    evidence["conditions"].append(clean_text)

                for t in tokens:
                    seen_tokens.add(t.i)

        ALLOWED_DEPS = {
            "amod",
            "compound",
            "pobj",
            "dobj",
            "attr",
            "acomp",
            "nsubj",
            "ROOT",
        }

        for token in doc:
            if token.i in seen_tokens:
                continue

            lemma = token.lemma_.lower()
            if is_negated(token):
                continue

            if token.dep_ not in ALLOWED_DEPS and token.pos_ not in {
                "NOUN",
                "VERB",
                "ADJ",
            }:
                continue

            if lemma in LIGHTING_TOKENS:
                phrase = expand_phrase(token)
                evidence["lighting"].append(phrase)
            elif lemma in WEATHER_TOKENS:
                phrase = expand_phrase(token)
                evidence["weather"].append(phrase)
            elif lemma in MATERIAL_TOKENS:
                evidence["materials"].append(lemma)
            elif lemma in CONDITION_TOKENS:
                evidence["conditions"].append(lemma)

        final = {}
        for k, v in evidence.items():
            counts = Counter(v)
            sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
            final[k] = [x[0] for x in sorted_items]

        return final
