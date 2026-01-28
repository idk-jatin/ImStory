import spacy
from fastcoref import spacy_component
from sentence_transformers import SentenceTransformer
from .page import PageDoc

PRONOUNS = {
    "i",
    "me",
    "we",
    "us",
    "you",
    "he",
    "him",
    "she",
    "her",
    "it",
    "they",
    "them",
    "mine",
    "ours",
    "yours",
    "his",
    "hers",
    "theirs",
    "its",
    "their",
    "myself",
    "ourselves",
    "yourself",
    "yourselves",
    "himself",
    "herself",
    "itself",
    "themselves",
    "oneself",
    "this",
    "that",
    "these",
    "those",
    "such",
    "one",
    "ones",
    "each",
    "either",
    "neither",
    "every",
    "none",
    "who",
    "whom",
    "whose",
    "which",
    "that",
    "each other",
    "one another",
    "everybody",
    "somebody",
    "nobody",
    "anybody",
    "someone",
    "no one",
    "anyone",
    "everything",
    "something",
    "nothing",
    "anything",
    "all",
    "some",
    "any",
    "both",
    "another",
    "much",
    "few",
    "little",
}


class NLPEngine:
    def __init__(self, device="cuda"):
        self.nlp = spacy.load("en_core_web_trf")
        self.nlp.add_pipe(
            "fastcoref",
            config={
                "model_architecture": "LingMessCoref",
                "model_path": "biu-nlp/lingmess-coref",
                "device": device,
            },
        )
        self.embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", device=device
        )

    # -----------------------------------------------------------------------------

    def analyze(self, page_num, text):
        page = PageDoc(page_num, text)

        doc = self.nlp(text, component_cfg={"fastcoref": {"resolve_text": True}})
        page.doc = doc
        page.sentences = [s.text.strip() for s in doc.sents]
        page.embedding = self.embedder.encode(text, normalize_embeddings=True)
        self.ext_ents(page)
        self.ext_corefs(page)
        self.ext_world(page)
        self.ext_noun(page)
        self.res_ents(page)

        return page

    # -----------------------------------------------------------------------------

    def ext_ents(self, page):
        ents = []
        for ent in page.doc.ents:
            ents.append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
            )
        page.entities = ents

    # -----------------------------------------------------------------------------

    def ext_corefs(self, page):
        clusters = []
        for cluster in page.doc._.coref_clusters:
            mentions = []

            for start, end in cluster:
                span = page.doc.char_span(
                    start_idx=start, end_idx=end, alignment_mode="contract"
                )
                if span is None:
                    continue
                text = span.text.strip()
                if len(text) < 2:
                    continue
                mentions.append(
                    {
                        "text": text,
                        "start": span.start_char,
                        "end": span.end_char,
                        "root": span.root.text,
                    }
                )

            if len(mentions) >= 2:
                clusters.append(mentions)

        page.coref_clusters = clusters

    # -----------------------------------------------------------------------------

    def res_ents(self, page):
        for ent in page.entities:
            name = ent["text"].strip()
            label = ent["label"]

            if label == "PERSON":
                self.register(page.characters, name, ent)
            elif label in ("GPE", "LOC", "FAC"):
                self.register(page.locations, name, ent)
            elif label in ("OBJECT", "PRODUCT", "EVENT", "WORK_OF_ART"):
                self.register(page.objects, name, ent)

    # -----------------------------------------------------------------------------

    def ext_world(self, page):
        world = []

        for cluster in page.coref_clusters:
            surface_forms = set(m["text"].lower() for m in cluster)
            roots = set(m["root"].lower() for m in cluster)

            head = self.canonical(cluster)

            world.append(
                {
                    "canonical": head,
                    "aliases": list(surface_forms),
                    "roots": list(roots),
                    "mentions": cluster,
                }
            )

        page.world_ents = world

    # -----------------------------------------------------------------------------

    def ext_noun(self, page):
        nouns = []
        for chunk in page.doc.noun_chunks:
            root = chunk.root
            if root.pos_ in ("NOUN", "PROPN"):
                if len(chunk.text) > 2:
                    nouns.append(
                        {
                            "text": chunk.text,
                            "root": root.text,
                            "start": chunk.start_char,
                            "end": chunk.end_char,
                        }
                    )
        page.noun_ents = nouns

    # -----------------------------------------------------------------------------

    def register(self, bucket, name, ent):
        if name not in bucket:
            bucket[name] = {"name": name, "mentions": []}
        bucket[name]["mentions"].append(ent)

    # -----------------------------------------------------------------------------

    def canonical(self, cluster):
        propn = [m for m in cluster if m["root"][0].isupper()]
        if propn:
            return max(propn, key=lambda x: len(x["text"]))["text"]

        non_pron = [m for m in cluster if m["text"].lower() not in PRONOUNS]

        if non_pron:
            return max(non_pron, key=lambda x: len(x["text"]))["text"]

        return max(cluster, key=lambda x: len(x["text"]))["text"]
