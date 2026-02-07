import math
from typing import Dict


class PageSalience:
    def __init__(
        self,
        page,
        primary_entities,
        active_relations,
        dominant_state,
        dominant_action,
        salience_scores,
    ):
        self.page = page
        self.primary_entities = primary_entities
        self.active_relations = active_relations
        self.dominant_state = dominant_state
        self.dominant_action = dominant_action
        self.salience_scores = salience_scores


# ------------------------------------------------------------


class Salience:

    CONTINUOUS_WEIGHT = 1.0
    ACTION_WEIGHT = 0.6
    PAGE_EVENT_BOOST = 0.3
    CONTEXT_BONUS = 0.15
    MAX_ENTITIES = 3
    RECENT_PAGE_BOOST = 3.5
    NEAR_PAGE_BOOST = 1.5
    DECAY_LAMBDA = 0.8

    def compute(self, page, world) -> PageSalience:
        page_num = page.pn
        active_relations = [r for r in world.relations if r.is_active(page_num)]

        scores: Dict[int, float] = {}

        for ent in world.ents.values():
            score = 0.0
            if ent.last_page is None:
                continue

            if ent.first_page is not None and ent.first_page > page_num:
                continue

            if ent.last_page < page_num - 1:
                continue

            if ent.kind == "ABSTRACT":
                continue
            if ent.kind == "CHARACTER":
                score += 2.5

            if ent.last_page == page_num:
                score += self.RECENT_PAGE_BOOST
            elif ent.last_page == page_num - 1:
                score += self.NEAR_PAGE_BOOST

            age = page_num - ent.last_page
            if age > 1:
                score *= math.exp(-self.DECAY_LAMBDA * (age - 1))

            if ent.first_page is not None and ent.last_page is not None:
                lifespan = ent.last_page - ent.first_page
                if lifespan > 0:
                    score += math.log1p(lifespan) * 0.5

            for r in active_relations:
                if r.source == ent or r.target == ent:
                    weight = (
                        self.CONTINUOUS_WEIGHT
                        if r.is_continuous
                        else self.ACTION_WEIGHT
                    )
                    score += r.confidence * weight

            for ev in page.events:
                if ev.subject == ent or ev.object == ent:
                    score += self.PAGE_EVENT_BOOST
                    break

            if ent in world.context(k=3):
                score += self.CONTEXT_BONUS

            if score > 0:
                scores[ent.id] = round(score, 3)

        ranked_entities = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        selected_entities = [
            world.ents[eid] for eid, _ in ranked_entities[: self.MAX_ENTITIES]
        ]

        for r in active_relations:
            if r.source.kind == "CHARACTER" and r.source not in selected_entities:
                selected_entities.insert(0, r.source)
            if r.target.kind == "CHARACTER" and r.target not in selected_entities:
                selected_entities.insert(0, r.target)

        seen = set()
        final_entities = []
        for e in selected_entities:
            if e.id not in seen:
                final_entities.append(e)
                seen.add(e.id)
            if len(final_entities) >= self.MAX_ENTITIES:
                break

        dominant_state = None
        dominant_action = None

        if active_relations:
            states = [r for r in active_relations if r.is_continuous]
            if states:
                dominant_state = max(states, key=lambda r: r.confidence)

            actions = [r for r in active_relations if not r.is_continuous]
            if actions:
                dominant_action = max(actions, key=lambda r: r.confidence)

        return PageSalience(
            page=page_num,
            primary_entities=final_entities,
            active_relations=active_relations,
            dominant_state=dominant_state,
            dominant_action=dominant_action,
            salience_scores=scores,
        )
