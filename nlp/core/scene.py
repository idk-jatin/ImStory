from .entity import Entity
from core.constants import SPATIAL_PREPS


class SceneFrame:
    def __init__(
        self,
        page,
        characters,
        objects,
        place,
        dominant_action,
        dominant_state,
        continuity,
        intensity,
        visualizable,
        spatial_relations=None,
    ):
        self.page = page
        self.characters = characters
        self.objects = objects
        self.place = place
        self.dominant_action = dominant_action
        self.dominant_state = dominant_state
        self.continuity = continuity
        self.intensity = intensity
        self.visualizable = visualizable
        self.spatial_relations = spatial_relations or []

    def __repr__(self):
        return (
            f"SceneFrame(page={self.page}, "
            f"chars={[c.name for c in self.characters]}, "
            f"objs={[o.name for o in self.objects]}, "
            f"place={self.place.name if self.place else None}, "
            f"continuity={self.continuity}, "
            f"intensity={round(self.intensity,2)}, "
            f"visualizable={self.visualizable})"
        )

    @property
    def focus_entities(self):
        return self.primary_entities

    @property
    def primary_entities(self):
        ents = []
        ents.extend(self.characters)
        ents.extend(self.objects)
        if self.place:
            ents.append(self.place)
        return ents


class SceneFrameBuilder:
    MAX_CHARACTERS = 2
    MAX_OBJECTS = 2

    def build(self, page, salience, world, prev_frame=None):
        characters = [
            e
            for e in salience.primary_entities
            if e.kind == "CHARACTER" and e.kind != "GROUP"
        ][: self.MAX_CHARACTERS]

        objects = [e for e in salience.primary_entities if e.kind == "OBJECT"][
            : self.MAX_OBJECTS
        ]

        place = next(
            (e for e in salience.primary_entities if e.kind == "PLACE"),
            None,
        )

        if place is None and prev_frame:
            place = prev_frame.place

        action = salience.dominant_action
        state = salience.dominant_state

        if action is None:
            for ev in page.events:
                if isinstance(ev.subject, Entity) or isinstance(ev.object, Entity):
                    action = ev
                    break

        if action and hasattr(action, "subject"):
            if isinstance(action.subject, Entity):
                if action.subject.kind != "CHARACTER":
                    action = None

        continuity = self._classify_continuity(action, state, prev_frame, place)
        base_conf = (
            action.confidence if (action and hasattr(action, "confidence")) else 0.2
        )

        dynamic_verbs = {
            "run",
            "jump",
            "fight",
            "attack",
            "fall",
            "shout",
            "explode",
            "crash",
        }
        is_dynamic = False
        if action and hasattr(action, "lemma") and action.lemma in dynamic_verbs:
            is_dynamic = True

        salience = 0.4 if is_dynamic else 0.0

        env_change = 0.3 if continuity == "transition" else 0.0

        intensity = base_conf + salience + env_change

        intensity = min(1.0, intensity)

        spatial = self._extract_spatial_relations(page, characters + objects)

        visualizable = intensity > 0.2

        return SceneFrame(
            page=page.pn,
            characters=characters,
            objects=objects,
            place=place,
            dominant_action=action,
            dominant_state=state,
            continuity=continuity,
            intensity=min(intensity, 1),
            visualizable=visualizable,
            spatial_relations=spatial,
        )

    def _classify_continuity(self, action, state, prev_frame, place):
        if prev_frame is None:
            return "enter"

        if prev_frame.place != place:
            return "transition"

        if action and prev_frame.dominant_action:
            if self._action_key(action) == self._action_key(prev_frame.dominant_action):
                return "hold"

        if state and prev_frame.dominant_state:
            if state.type == prev_frame.dominant_state.type:
                return "hold"

        return "transition"

    def _action_key(self, action):
        if action is None:
            return None
        if hasattr(action, "lemma"):
            return action.lemma
        if hasattr(action, "type"):
            return action.type
        return None

    def _extract_spatial_relations(self, page, entities):
        if not page.doc:
            return []

        relations = []

        ent_heads = {}
        for ent in entities:
            for token in page.doc:
                if (
                    token.text.lower() in ent.aliases
                    or token.text.lower() in ent.name.lower().split()
                ):
                    if token.pos_ in {"NOUN", "PROPN", "PRON"}:
                        ent_heads[token] = ent

        for head_tok, subject in ent_heads.items():
            for child in head_tok.children:
                if child.dep_ == "prep":
                    prep = child.lemma_
                    if prep in SPATIAL_PREPS:
                        for pobj in child.children:
                            if pobj.dep_ == "pobj" and pobj in ent_heads:
                                object_ent = ent_heads[pobj]
                                if object_ent != subject:
                                    relations.append((subject, prep, object_ent))

            if head_tok.head.pos_ == "VERB":
                verb = head_tok.head
                for child in verb.children:
                    if child.dep_ == "prep":
                        prep = child.lemma_
                        if prep in SPATIAL_PREPS:
                            for pobj in child.children:
                                if pobj.dep_ == "pobj" and pobj in ent_heads:
                                    object_ent = ent_heads[pobj]
                                    if object_ent != subject:
                                        relations.append((subject, prep, object_ent))

        return list(set(relations))
