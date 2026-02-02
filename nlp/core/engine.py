import spacy
from fastcoref import spacy_component
from sentence_transformers import SentenceTransformer
from .page import PageDoc


PRONOUNS = {
    "i","me","we","us","you","he","him","she","her","it","they","them",
    "mine","ours","yours","his","hers","theirs","its","their",
    "myself","ourselves","yourself","yourselves","himself","herself",
    "itself","themselves","oneself",
    "this","that","these","those","such","one","ones",
    "each","either","neither","every","none",
    "who","whom","whose","which",
    "each other","one another",
    "everybody","somebody","nobody","anybody","someone","no one","anyone",
    "everything","something","nothing","anything",
    "all","some","any","both","another","much","few","little",
}


def is_pronoun(text: str) -> bool:
    return " ".join(text.lower().split()) in PRONOUNS


class NLPEngine:
    def __init__(self, device="cuda"):
        self.nlp = spacy.load("en_core_web_trf")

        self.nlp.add_pipe(
            "fastcoref",
            after="ner",
            config={
                "model_architecture": "LingMessCoref",
                "model_path": "biu-nlp/lingmess-coref",
                "device": device,
            },
        )

        self.embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device=device,
        )

    # -------------------------------------------------------------------------

    def analyze(self, page_num, text):
        page = PageDoc(page_num, text)

        doc = self.nlp(text,component_cfg={"fastcoref": {"resolve_text": False}})

        page.doc = doc
        page.resolved_text = doc._.resolved_text

        page.sentences = [
            {"sid": i, "text": s.text.strip()}
            for i, s in enumerate(doc.sents)
        ]

        page.embedding = self.embedder.encode(
            text, normalize_embeddings=True
        )

        self.ext_ents(page)
        self.ext_corefs(page)
        self.ext_world(page)
        self.ext_noun(page)
        self.res_ents(page)

        return page

    # -------------------------------------------------------------------------

    def ext_ents(self, page):
        ents = []
        for ent in page.doc.ents:
            ents.append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "sent_token_start": ent.sent.start,
                    "token_start": ent.start,
                }
            )
        page.entities = ents

    # -------------------------------------------------------------------------

    def ext_corefs(self, page):
        clusters = []

        for cluster in page.doc._.coref_clusters:
            mentions = []

            for start, end in cluster:
                span = page.doc.char_span(
                    start, end, alignment_mode="contract"
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
                        "lemma": span.root.lemma_,
                        "pos": span.root.pos_,
                    }
                )

            if len(mentions) >= 2:
                clusters.append(mentions)

        page.coref_clusters = clusters

    # -------------------------------------------------------------------------

    def ext_world(self, page):
        world = []

        for cluster in page.coref_clusters:
            aliases = {m["text"].lower() for m in cluster}
            roots = {m["lemma"].lower() for m in cluster}

            canonical = self.canonical(cluster)
            if canonical is None:
                continue

            world.append(
                {
                    "canonical": canonical,
                    "aliases": list(aliases),
                    "roots": list(roots),
                    "mentions": cluster,
                }
            )

        page.world_ents = world

    # -------------------------------------------------------------------------

    def ext_noun(self, page):
        nouns = []

        for chunk in page.doc.noun_chunks:
            root = chunk.root

            if root.pos_ not in ("NOUN", "PROPN"):
                continue

            if root.dep_ not in ("nsubj", "dobj", "pobj"):
                continue

            text = chunk.text.strip()
            if len(text) < 3:
                continue

            nouns.append(
                {
                    "text": text,
                    "root": root.text,
                    "lemma": root.lemma_,
                    "start": chunk.start_char,
                    "end": chunk.end_char,
                }
            )

        page.noun_ents = nouns

    # -------------------------------------------------------------------------

    def res_ents(self, page):
        for ent in page.world_ents:
            name = ent["canonical"]

            self.register(page.characters, name, ent)

    # -------------------------------------------------------------------------

    def register(self, bucket, name, ent):
        if name not in bucket:
            bucket[name] = {
                "name": name,
                "mentions": [],
                "aliases": set(),
            }

        bucket[name]["mentions"].extend(ent["mentions"])
        bucket[name]["aliases"].update(ent["aliases"])

    # -------------------------------------------------------------------------

    def canonical(self, cluster):
        propn = [
            m for m in cluster
            if m["text"][0].isupper()
            and not is_pronoun(m["text"])
            and len(m["text"]) > 2
        ]

        if propn:
            return max(propn, key=lambda x: len(x["text"]))["text"]

        non_pron = [
            m for m in cluster
            if not is_pronoun(m["text"])
        ]

        if non_pron:
            return max(non_pron, key=lambda x: len(x["text"]))["text"]

        return None
