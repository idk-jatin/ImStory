import nltk

AGENTIVE_DOMAINS = {
    "verb.cognition",
    "verb.communication",
    "verb.emotion",
    "verb.perception",
    "verb.social",
    "verb.competition",
    "verb.consumption",
    "verb.body",
}


class Typer:

    def __init__(self):
        print("Loading Semantic Typing Engine (WordNet)...")

        try:
            nltk.data.find("corpora/wordnet.zip")
        except LookupError:
            print("Downloading WordNet...")
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)

        from nltk.corpus import wordnet

        self.wn = wordnet

    def infer(self, entity, world):

        if self._check_verb_semantics(entity, world):
            return "CHARACTER"

        noun_type = self._check_noun_semantics(entity)
        if noun_type:
            return noun_type

        for ev in world.events:
            if ev.subject == entity:
                print(
                    f"   ? [AGENCY] {entity.name}: CHARACTER " f"(named agent fallback)"
                )
                return "CHARACTER"

        return "OBJECT"

    def _check_verb_semantics(self, entity, world):

        for ev in world.events:
            if ev.subject != entity:
                continue

            synsets = self.wn.synsets(ev.lemma.lower(), pos=self.wn.VERB)
            if not synsets:
                continue

            domain = synsets[0].lexname()

            if domain == "verb.perception" and ev.object is None:
                continue

            if domain in AGENTIVE_DOMAINS:
                if self._has_persistent_agency(entity, world):
                    print(
                        f"   ? [BEHAVIOR] {entity.name}: CHARACTER "
                        f"(persistent agent)"
                    )
                    return True

        return False

    def _has_persistent_agency(self, entity, world, min_events=2):
        count = 0

        for ev in world.events:
            if ev.subject != entity:
                continue

            synsets = self.wn.synsets(ev.lemma.lower(), pos=self.wn.VERB)
            if not synsets:
                continue

            if synsets[0].lexname() in AGENTIVE_DOMAINS:
                count += 1

        return count >= min_events

    def _check_noun_semantics(self, entity):

        head = entity.name.split()[-1].lower()
        synsets = self.wn.synsets(head)

        if not synsets:
            return None

        primary = synsets[0]
        lex = primary.lexname()

        if "person" in lex or "animal" in lex:
            return "CHARACTER"

        if "location" in lex or "group" in lex:
            return "PLACE"

        if "artifact" in lex or "object" in lex:
            return "OBJECT"

        if primary.hypernym_paths():
            hypers = {h.name() for path in primary.hypernym_paths() for h in path}
            if "location.n.01" in hypers:
                return "PLACE"

        if any(k in lex for k in ("attribute", "time", "cognition")):
            return "ABSTRACT"

        return "OBJECT"
