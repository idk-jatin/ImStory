import re
from sklearn.metrics.pairwise import cosine_similarity

from .entity import Entity
from .events import EventExtractor
from .linker import resolve
from core.constants import GROUP_INDICATORS


class World:
    def __init__(self, sim_ts=0.75):
        self.ents = {}
        self.page_ind = {}
        self.counter = 0
        self.sim_ts = sim_ts
        self.pages = {}
        self.timeline = []
        self.events = []
        self.relations = []

        self.extractor = EventExtractor()

    # ------------------------------------------------------------------

    def new_ent(self, name, kind, mention, page, embedding=None, doc=None):
        self.counter += 1
        ent = Entity(self.counter, name, kind, embedding)
        ent.update(mention, page, embedding, doc=doc)
        self.ents[self.counter] = ent
        return ent

    # ------------------------------------------------------------------

    def freeze_types(self, typer):

        for ent in self.ents.values():
            if ent.kind == "GROUP":
                continue

            final_type = typer.infer_and_lock(ent, self)
            ent.kind = final_type
            typer.finalize(ent)

            if hasattr(ent, "type_scores"):
                top_score = max(ent.type_scores.values()) if ent.type_scores else 0
                print(
                    f"Locked ID {ent.id} [{ent.name}] -> {ent.kind} (Score: {top_score})"
                )

    def sim_ent(self, name, embedding=None, attributes=None):

        def normalize(txt):
            txt = txt.lower().strip()
            txt = re.sub(r"^(a|an|the)\s+", "", txt)
            return txt

        name_raw = name.lower().strip()
        name_norm = normalize(name_raw)
        name_head = name_norm.split()[-1] if name_norm else ""

        def last_token(txt):
            parts = txt.split()
            return parts[-1] if parts else ""

        candidates = []

        for ent in self.ents.values():
            score = 0

            if normalize(ent.name) == name_norm:
                score += 10
            elif ent.name.lower() == name_raw:
                score += 9

            elif name_raw in ent.aliases:
                score += 8
            elif any(normalize(a) == name_norm for a in ent.aliases):
                score += 7

            elif any(last_token(normalize(a)) == name_head for a in ent.aliases):
                score += 3

            if score == 0:
                continue

            if embedding is not None and ent.embeddings:
                sim = cosine_similarity([ent.mean_emb()], [embedding])[0][0]
                if sim < 0.6:
                    continue

            if attributes:
                temp = Entity(-1, name)
                temp.attributes.update(attributes)
                if not ent.compatible_with(temp):
                    continue

            candidates.append((ent, score))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    GROUP_INDICATORS = GROUP_INDICATORS

    def clean_possessive(self, name):
        return re.sub(r"'s?$|’s?$", "", name).strip()

    def is_group(self, name):
        parts = {p.lower() for p in name.split()}
        return bool(parts & self.GROUP_INDICATORS)

    # ------------------------------------------------------------------

    def register(self, canonical, kind, mention, page, embedding=None):
        attributes = {}

        canonical = self.clean_possessive(canonical)

        doc = self.pages[page].doc
        span = doc.char_span(mention["start"], mention["end"], alignment_mode="expand")

        if span:
            from collections import defaultdict

            attrs = defaultdict(set)
            for tok in span.root.children:
                if tok.dep_ == "amod":
                    attrs["appearance"].add(tok.lemma_)
                elif tok.dep_ == "appos":
                    attrs["role"].add(tok.text.lower())
            attributes = attrs

        ent = self.sim_ent(canonical, embedding, attributes)

        if ent and attributes:
            temp = Entity(-1, canonical)
            temp.attributes.update(attributes)
            if not ent.compatible_with(temp):
                ent = None

        if ent:
            ent.update(mention, page, embedding, doc=self.pages[page].doc)
        else:
            if self.is_group(canonical):
                kind = "GROUP"

            ent = self.new_ent(
                canonical,
                kind,
                mention,
                page,
                embedding,
                doc=self.pages[page].doc,
            )
        return ent

    # ------------------------------------------------------------------

    def r_page(self, page):
        self.pages[page.pn] = page
        seen = set()

        mention_map = {}

        for group in page.world_ents:
            canonical = group["canonical"]
            mentions = group["mentions"]

            for m in mentions:
                ent = self.register(
                    canonical=canonical,
                    kind="unknown",
                    mention=m,
                    page=page.pn,
                    embedding=None,
                )
                seen.add(ent.id)
                mention_map[(m["start"], m["end"])] = ent

        self.page_ind[page.pn] = list(seen)

        if not self.timeline or self.timeline[-1] != page.pn:
            self.timeline.append(page.pn)

        self.extractor.extract(page, world=self)

        for ev in page.events:
            ev.subject = resolve(ev.subject, mention_map)
            ev.object = resolve(ev.object, mention_map)
            ev.indirect = resolve(ev.indirect, mention_map)
            ev.location = resolve(ev.location, mention_map)

            if isinstance(ev.object, dict) and "alias" in ev.object:
                if hasattr(ev.subject, "aliases"):
                    ev.subject.aliases.add(ev.object["alias"].lower())

        self.events.extend(page.events)

    # ------------------------------------------------------------------

    def context(self, k=3):
        ctx = []
        for p in self.timeline[-k:]:
            for eid in self.page_ind.get(p, []):
                ctx.append(self.ents[eid])
        return list({e.id: e for e in ctx}.values())
