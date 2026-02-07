from .event import Event

from core.constants import LOCATION_PREPOSITIONS


class EventExtractor:
    def extract(self, page, world=None):
        events = []

        for sent in page.doc.sents:
            for token in sent:
                if token.pos_ != "VERB":
                    continue
                if token.dep_ in ("aux", "auxpass"):
                    continue

                subj = self.resolve_entity(self.find_subj(token), world)
                if subj is None:
                    continue

                obj = self.resolve_entity(self.find_obj(token), world)
                iobj = self.resolve_entity(self.find_iobj(token), world)
                loc = self.resolve_entity(self.find_loc(token), world)

                if obj is None and iobj is not None:
                    obj, iobj = iobj, None

                ev = Event(
                    verb=token,
                    subj=subj,
                    obj=obj,
                    iobj=iobj,
                    location=loc,
                    sentence=sent.text,
                    page=page.pn,
                )
                events.append(ev)

        page.events = events
        return page

    # ----------------------------

    def resolve_entity(self, token, world):
        if token is None or world is None:
            return token

        text = token.text.lower()

        for ent in world.ents.values():
            if text == ent.name.lower() or text in ent.aliases:
                return ent

        return token

    def find_subj(self, verb):
        for c in verb.children:
            if c.dep_ in ("nsubj", "nsubjpass"):
                return c

    def find_obj(self, verb):
        for c in verb.children:
            if c.dep_ in ("dobj", "obj", "attr", "oprd"):
                return c

    def find_iobj(self, verb):
        for c in verb.children:
            if c.dep_ == "dative":
                return c

        for c in verb.children:
            if c.dep_ == "prep" and c.text.lower() == "to":
                for pobj in c.children:
                    if pobj.dep_ == "pobj":
                        return pobj

    def find_loc(self, verb):
        for prep in verb.children:
            if prep.dep_ == "prep" and prep.text.lower() in LOCATION_PREPOSITIONS:
                for pobj in prep.children:
                    if pobj.dep_ == "pobj":
                        return pobj
