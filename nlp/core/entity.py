import numpy as np
from collections import defaultdict

from core.constants import PRONOUNS, CLOTHING_KEYWORDS


def is_pronoun(text: str):
    return " ".join(text.lower().split()) in PRONOUNS


class Entity:
    def __init__(self, eid, name, kind="unknown", embedding=None):
        self.id = eid
        self.name = name
        self.kind = kind

        self.aliases = {name.lower()}
        self.mentions = []

        self.first_page = None
        self.last_page = None

        self.embeddings = []

        self.attributes = defaultdict(set)

        self.appearance_history = []
        self.clothing = []
        self.object_condition = []
        self.location_last_seen = None

        self.hair = set()
        self.face = set()
        self.color_palette = set()

        if embedding is not None:
            self.embeddings.append(embedding)

    # ---------------------------------------------------------------------

    def update(self, mention, page_num, embedding=None, doc=None):
        self.mentions.append(mention)

        text = mention["text"].lower()

        if not is_pronoun(text.split()[0]):
            self.aliases.add(text)

        if self.first_page is None:
            self.first_page = page_num
        self.last_page = page_num

        if embedding is not None:
            self.embeddings.append(embedding)

        if doc is not None:
            span = doc.char_span(
                mention["start"], mention["end"], alignment_mode="expand"
            )
            if span:
                self._extract_attributes(span, page_num)

    def add_clothing(self, desc, page, conf=1.0):
        for item in self.clothing:
            if item["desc"] == desc:
                item["page"] = page
                item["conf"] = min(1.0, item["conf"] + 0.2)
                return

        self.clothing.append({"desc": desc, "page": page, "conf": conf})
        self.clothing.sort(key=lambda x: x["page"], reverse=True)

    # ---------------------------------------------------------------------

    def attribute_signature(self):
        sig = {}

        for k, vals in self.attributes.items():
            if vals:
                sig[k] = sorted(vals)

        return sig

    # ---------------------------------------------------------------------

    def compatible_with(self, other):
        my_sig = self.attribute_signature()
        ot_sig = other.attribute_signature()

        for key in set(my_sig) & set(ot_sig):
            if set(my_sig[key]) != set(ot_sig[key]):
                return False

        return True

    CLOTHING_KEYWORDS = CLOTHING_KEYWORDS

    def _extract_attributes(self, span, page_num):
        root = span.root

        for tok in root.children:
            lemma = tok.lemma_.lower()
            dep = tok.dep_

            if dep == "amod":

                if lemma.endswith("ed") or lemma in {"wet", "dirty", "clean", "rough"}:
                    self.attributes["condition"].add(lemma)
                else:

                    head_noun = tok.head.text.lower()
                    if head_noun in {"hair", "locks", "curls", "braids"}:
                        self.hair.add(f"{lemma} {head_noun}")
                    elif head_noun in {"face", "eyes", "expression", "gaze"}:
                        self.face.add(f"{lemma} {head_noun}")
                    elif lemma in {
                        "red",
                        "blue",
                        "green",
                        "black",
                        "white",
                        "grey",
                        "yellow",
                        "purple",
                        "orange",
                        "brown",
                        "gold",
                        "silver",
                        "dark",
                        "pale",
                    }:
                        self.color_palette.add(lemma)

                    self.attributes["appearance"].add(lemma)

            elif dep == "appos":
                self.attributes["role"].add(tok.text.lower())
            elif dep == "compound":
                self.attributes["material"].add(lemma)

            elif dep == "prep":
                child = next(tok.children, None)
                if child:
                    child_lemma = child.lemma_.lower()
                    if lemma == "of":
                        self.attributes["material"].add(child_lemma)
                    elif lemma == "in":

                        self.attributes["spatial"].add(f"in {child_lemma}")
                        if child_lemma in self.CLOTHING_KEYWORDS:
                            self.add_clothing(child_lemma, page_num)

                    elif lemma == "with":
                        self.attributes["spatial"].add(f"with {child_lemma}")
                    elif lemma == "on":
                        self.attributes["spatial"].add(f"on {child_lemma}")
                    elif lemma == "wearing":
                        self.add_clothing(child_lemma, page_num)

            elif dep == "nmod":
                self.attributes["condition"].add(lemma)

        head = root.head
        if (
            head
            and head.pos_ in {"VERB", "AUX"}
            and root.dep_ in {"nsubj", "nsubjpass"}
        ):
            for child in head.children:
                if child.dep_ in {"acomp", "attr"}:
                    self.attributes["state"].add(child.lemma_.lower())

    # ---------------------------------------------------------------------

    def mean_emb(self):
        if not self.embeddings:
            return None
        return np.mean(np.vstack(self.embeddings), axis=0)

    # ---------------------------------------------------------------------

    def about(self):
        return (
            f"Entity:{self.name} | Kind:{self.kind} | "
            f"Pages:{self.first_page}-{self.last_page}"
        )

    def __repr__(self):
        return self.name
