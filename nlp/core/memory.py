import re
from sklearn.metrics.pairwise import cosine_similarity

from .entity import Entity
from .events import EventExtractor
from .linker import resolve


class World:
    def __init__(self, sim_ts=0.75):
        self.ents = {}          
        self.page_ind = {}     
        self.counter = 0
        self.sim_ts = sim_ts

        self.timeline = []
        self.events = []  
        self.relations = []

        self.extractor = EventExtractor()

    # ------------------------------------------------------------------

    def new_ent(self, name, kind, mention, page, embedding=None):
        self.counter += 1
        ent = Entity(self.counter, name, kind, embedding)
        ent.update(mention, page, embedding)
        self.ents[self.counter] = ent
        return ent

    # ------------------------------------------------------------------

    def freeze_types(self, typer):
        """
        Forces all entities to resolve their type based on accumulated evidence
        and locks them to prevent future degradation.
        """
        print("\n--- LOCKING ONTOLOGY ---")
        for ent in self.ents.values():
            final_type = typer.infer_and_lock(ent, self)
            ent.kind = final_type
            typer.finalize(ent)
            
            if hasattr(ent, "type_scores"):
                top_score = max(ent.type_scores.values()) if ent.type_scores else 0
                print(f"Locked ID {ent.id} [{ent.name}] -> {ent.kind} (Score: {top_score})")


    def sim_ent(self, name, embedding=None):
        def normalize(txt):
            txt = txt.lower().strip()
            txt = re.sub(r"^(a|an|the)\s+", "", txt)
            return txt

        name_raw = name.lower().strip()
        name_norm = normalize(name_raw)
        name_head = name_norm.split()[-1]

        for ent in self.ents.values():
            if name_raw in ent.aliases:
                return ent

            for a in ent.aliases:
                if normalize(a) == name_norm:
                    return ent

            for a in ent.aliases:
                if normalize(a).split()[-1] == name_head:
                    return ent

            if embedding is not None and ent.mean_emb() is not None:
                sim = cosine_similarity(
                    [embedding], [ent.mean_emb()]
                )[0][0]
                if sim >= self.sim_ts:
                    return ent

        return None

    # ------------------------------------------------------------------

    def register(self, canonical, kind, mention, page, embedding=None):
        ent = self.sim_ent(canonical, embedding)
        if ent:
            ent.update(mention, page, embedding)
        else:
            ent = self.new_ent(canonical, kind, mention, page, embedding)
        return ent

    # ------------------------------------------------------------------

    def r_page(self, page):
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

        self.extractor.extract(page)

        for ev in page.events:
            ev.subject = resolve(ev.subject, mention_map)
            ev.object = resolve(ev.object, mention_map)
            ev.indirect = resolve(ev.indirect, mention_map)
            ev.location = resolve(ev.location, mention_map)

        self.events.extend(page.events)

    # ------------------------------------------------------------------

    def context(self, k=3):
        ctx = []
        for p in self.timeline[-k:]:
            for eid in self.page_ind.get(p, []):
                ctx.append(self.ents[eid])
        return list({e.id: e for e in ctx}.values())