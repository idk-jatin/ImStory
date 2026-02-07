import math

from core.constants import (
    CONTINUOUS_TYPES,
    STATE_HALF_LIFE,
    ACTION_HALF_LIFE,
    MAX_STATE_PERSIST,
    SPAN_BOOST_SCALE,
)


class Relation:
    def __init__(self, source, rel_type, target, page, verb, sentence):
        self.source = source
        self.target = target
        self.type = rel_type

        self.start_page = page
        self.end_page = page
        self.last_mentioned_page = page

        self.support = 1
        self.verbs = {verb}
        self.sentences = [sentence]

        self.is_continuous = rel_type in CONTINUOUS_TYPES
        self.confidence = 0.0

    # ------------------------------------------------------------

    def reinforce(self, page, verb, sentence):
        self.support += 1
        self.verbs.add(verb)
        self.sentences.append(sentence)

        if page > self.end_page:
            self.end_page = page
        self.last_mentioned_page = page

    # ------------------------------------------------------------

    def compute_confidence(self):

        score = 1 - math.exp(-0.5 * self.support)

        span = self.end_page - self.start_page
        if span > 0:
            score += math.log1p(span) * SPAN_BOOST_SCALE

        self.confidence = round(min(score, 1.0), 2)

    # ------------------------------------------------------------

    def is_active(self, current_page):

        delta = current_page - self.last_mentioned_page
        if delta < 0:
            return False

        if not self.is_continuous:
            decay = math.exp(-delta / ACTION_HALF_LIFE)
            return decay > 0.5

        if delta > MAX_STATE_PERSIST:
            return False

        decay = math.exp(-delta / STATE_HALF_LIFE)
        return decay > 0.3

    # ------------------------------------------------------------

    def __repr__(self):
        kind = "STATE" if self.is_continuous else "ACTION"
        return (
            f"<{kind} {self.source.name}->{self.target.name} "
            f"Conf:{self.confidence}>"
        )


class Promoter:
    def __init__(self):
        self.relations = {}

    # ------------------------------------------------------------

    def promote(self, raw_relations):
        for r in raw_relations:
            key = (r["source_id"], r["type"], r["target_id"])

            if key in self.relations:
                self.relations[key].reinforce(r["page"], r["verb"], r["sentence"])
            else:
                self.relations[key] = Relation(
                    r["source_obj"],
                    r["type"],
                    r["target_obj"],
                    r["page"],
                    r["verb"],
                    r["sentence"],
                )

        for rel in self.relations.values():
            rel.compute_confidence()

        return sorted(self.relations.values(), key=lambda r: r.confidence, reverse=True)

    # ------------------------------------------------------------

    def print_graph(self, promoted_relations):
        print("\n=== PROMOTED STORY FACTS ===")
        print(
            f"{'SOURCE':<15} | {'RELATION':<12} | "
            f"{'TARGET':<15} | {'KIND':<6} | {'CONF'}"
        )
        print("-" * 80)
        for r in promoted_relations:
            kind = "STATE" if r.is_continuous else "ACTION"
            print(
                f"{r.source.name:<15} | "
                f"{r.type:<12} | "
                f"{r.target.name:<15} | "
                f"{kind:<6} | "
                f"{r.confidence}"
            )
