from .event import Event

LP = {
    "in", "on", "at", "into", "toward", "towards", "from",
    "near", "inside", "outside", "beside", "through", "under", "over"
}
class EventExtractor:
    def extract(self, page):
        events = []
        for sent in page.doc.sents:
            for token in sent:
                if token.pos_ != "VERB": continue
                if token.dep_ in ("aux", "auxpass"): continue

                subj = self.find_subj(token)
                if subj is None: continue

                obj = self.find_obj(token)
                iobj = self.find_iobj(token) 
                loc = self.find_loc(token)

                if obj is None and iobj is not None:
                    obj = iobj
                    iobj = None

                ev = Event(
                    verb=token, subj=subj, obj=obj, iobj=iobj,
                    location=loc, sentence=sent.text, page=page.pn,
                )
                events.append(ev)

        page.events = events
        return page

    def find_subj(self, verb):
        for c in verb.children:
            if c.dep_ in ("nsubj", "nsubjpass"): return c
        return None

    def find_obj(self, verb):
        for c in verb.children:
            if c.dep_ in ("dobj", "obj", "attr", "oprd"): return c
        return None

    def find_iobj(self, verb):
       
        for c in verb.children:
            if c.dep_ == "dative":
                return c
        
        for c in verb.children:
            if c.dep_ == "prep" and c.text.lower() == "to":
                for pobj in c.children:
                    if pobj.dep_ == "pobj":
                        return pobj
        return None

    def find_loc(self, verb):
        for prep in verb.children:
            if prep.dep_ == "prep" and prep.text.lower() in LP:
                for pobj in prep.children:
                    if pobj.dep_ == "pobj": return pobj
        return None