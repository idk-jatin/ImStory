class Event:
    def __init__(
        self,
        verb,
        subj=None,
        obj=None,
        iobj=None,
        location=None,
        modifiers=None,
        sentence=None,
        page=None,
    ):
        self.verb_token = verb
        self.verb = verb.text
        self.lemma = verb.lemma_
        self.tense = verb.morph.get("Tense") or []
        self.subject = subj
        self.object = obj
        self.indirect = iobj
        self.location = location
        self.modifiers = modifiers or {}
        self.sentence = sentence
        self.page = page

    def __repr__(self):
        def fmt(x):
            if hasattr(x, "name"):
                return x.name
            if hasattr(x, "text"):
                return x.text
            return str(x)

        return (
            f"<Event {self.lemma} | "
            f"{fmt(self.subject)} → {fmt(self.object)} @ {fmt(self.location)}>"
        )
