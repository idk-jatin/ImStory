import nltk
from collections import defaultdict

from core.constants import (
    SCORE_NOUN_MATCH,
    SCORE_VERB_AGENT,
    SCORE_VERB_MOTION,
    SCORE_FALLBACK,
    TYPE_HIERARCHY,
    AGENTIVE_DOMAINS,
    PERSON_NOUNS,
    PLACE_NOUNS,
    OBJECT_NOUNS,
    REPRESENTATION_NOUNS,
    INTENTIONAL_VERBS,
    PHYSICAL_VERBS,
    LIGHT_OBJECTS,
    NATURAL_ELEMENTS,
)


class Typer:
    def __init__(self):
        print("Loading Evidence-Based Typing Engine...")
        try:
            nltk.data.find("corpora/wordnet.zip")
        except LookupError:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
        from nltk.corpus import wordnet

        self.wn = wordnet

    def infer_and_lock(self, entity, world):

        if not hasattr(entity, "type_scores"):
            entity.type_scores = defaultdict(float)
            entity.locked = False

        if getattr(entity, "locked", False):
            return entity.kind

        if entity.kind == "GROUP":
            return "GROUP"

        self._score_noun_semantics(entity, world)
        self._score_verb_semantics(entity, world)

        self._check_visual_attributes(entity)

        if not entity.type_scores:
            entity.kind = "ABSTRACT"
            return entity.kind

        best_type = max(entity.type_scores, key=entity.type_scores.get)
        best_score = entity.type_scores[best_type]

        current_type = entity.kind
        curr_level = TYPE_HIERARCHY.get(current_type, 0)
        new_level = TYPE_HIERARCHY.get(best_type, 0)

        if new_level >= curr_level:
            entity.kind = best_type

        page_stability = 0
        if hasattr(entity, "mentions"):
            page_stability = len(entity.mentions)

        if best_score > 8.0 or page_stability > 5:
            self.finalize(entity)

        return entity.kind

    def finalize(self, entity):
        entity.locked = True

    def _score_noun_semantics(self, entity, world=None):
        head = entity.name.split()[-1].lower()

        if head in PERSON_NOUNS:
            entity.type_scores["CHARACTER"] += SCORE_NOUN_MATCH
            return
        if head in PLACE_NOUNS:
            entity.type_scores["PLACE"] += SCORE_NOUN_MATCH
            return

        if head in REPRESENTATION_NOUNS:
            entity.type_scores["OBJECT"] += SCORE_NOUN_MATCH * 2.0
            return

        synsets = self.wn.synsets(head)
        if not synsets:
            return

        votes = defaultdict(float)

        for i, syn in enumerate(synsets[:3]):
            weight = 1.0 / (i + 1)
            lex = syn.lexname()

            if any(
                x in lex
                for x in [
                    "time",
                    "cognition",
                    "feeling",
                    "state",
                    "phenomenon",
                    "attribute",
                ]
            ):
                votes["ABSTRACT"] += weight
            elif "person" in lex or "animal" in lex:
                votes["CHARACTER"] += weight
            elif "group" in lex:
                votes["CHARACTER"] += weight * 0.5
            elif "location" in lex:
                votes["PLACE"] += weight
            elif "artifact" in lex or "object" in lex:
                votes["OBJECT"] += weight

            for path in syn.hypernym_paths():
                for h in path:
                    if h.name() == "location.n.01":
                        votes["PLACE"] += weight

        best_vote = max(votes, key=votes.get) if votes else None
        if best_vote:
            entity.type_scores[best_vote] += SCORE_NOUN_MATCH * votes[best_vote]

        if votes["OBJECT"] > 0.8:
            entity.type_scores["CHARACTER"] = min(entity.type_scores["CHARACTER"], 2.0)

        if head in LIGHT_OBJECTS:
            entity.type_scores["OBJECT"] += 10.0
            entity.type_scores["CHARACTER"] -= 5.0

        if head in ["silhouette", "figure", "shape", "shadow"]:
            is_spatial_container = False
            if (
                world
                and hasattr(entity, "attributes")
                and "spatial" in entity.attributes
            ):
                for sp in entity.attributes["spatial"]:  # "in X", "at X"
                    if (
                        sp.startswith("in ")
                        or sp.startswith("at ")
                        or sp.startswith("inside ")
                    ):
                        is_spatial_container = True

            if is_spatial_container:
                entity.type_scores["PLACE"] += 3.0
            else:
                entity.type_scores["CHARACTER"] += 2.0

    def _score_verb_semantics(self, entity, world):
        if not hasattr(world, "events"):
            return

        for ev in world.events:
            if not hasattr(ev, "subject") or not hasattr(ev, "lemma"):
                continue
            if ev.subject != entity:
                continue

            synsets = self.wn.synsets(ev.lemma.lower(), pos=self.wn.VERB)
            if not synsets:
                continue

            domain = synsets[0].lexname()

            if domain == "verb.perception" and ev.object is None:
                continue

            if domain in AGENTIVE_DOMAINS:
                head = entity.name.split()[-1].lower()
                is_metaphor = head in NATURAL_ELEMENTS and domain in {
                    "verb.communication",
                    "verb.cognition",
                }

                if not is_metaphor:
                    if ev.lemma.lower() in INTENTIONAL_VERBS:
                        entity.type_scores["CHARACTER"] += SCORE_VERB_AGENT * 1.5
                    elif ev.lemma.lower() in PHYSICAL_VERBS:
                        pass
                    else:
                        entity.type_scores["CHARACTER"] += SCORE_VERB_AGENT

            elif domain == "verb.motion":
                if self.is_intentional_agent(entity):
                    entity.type_scores["CHARACTER"] += SCORE_VERB_MOTION
                elif entity.type_scores["CHARACTER"] > 0:
                    entity.type_scores["CHARACTER"] += SCORE_VERB_MOTION

            if ev.object and hasattr(ev.object, "kind") and ev.object.kind == "OBJECT":
                if domain in {"verb.contact", "verb.creation", "verb.possession"}:
                    if ev.lemma.lower() not in PHYSICAL_VERBS:
                        entity.type_scores["CHARACTER"] += 2.0

    def _check_visual_attributes(self, entity):
        if hasattr(entity, "clothing") and entity.clothing:
            entity.type_scores["CHARACTER"] += 4.0

        if hasattr(entity, "attributes"):
            if "appearance" in entity.attributes:
                for adj in entity.attributes["appearance"]:
                    if adj in {
                        "tired",
                        "happy",
                        "sad",
                        "angry",
                        "young",
                        "old",
                        "busy",
                    }:
                        entity.type_scores["CHARACTER"] += 3.0

    def is_intentional_agent(self, entity):
        return entity.type_scores["CHARACTER"] > entity.type_scores["OBJECT"]
