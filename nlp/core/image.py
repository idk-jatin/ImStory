from core.constants import (
    ATMOSPHERE_ANTONYMS,
    RELATION_VERBS,
    VISUAL_VERBS,
    ABSTRACT_MAP,
    ATMOSPHERE_CLUSTERS,
    ATM_PHRASES,
    LIGHTING_TEMPLATES,
)


class VisualWorldState:

    def __init__(self):
        self.place = None
        self.lighting = None
        self.atmosphere = set()
        self.atmosphere_scores = {}
        self.last_known_clothing = {}

        self.ATMOSPHERE_ANTONYMS = ATMOSPHERE_ANTONYMS

    def update_from_scene(self, scene):
        if scene.place is not None:
            new_name = (
                scene.place.name if hasattr(scene.place, "name") else str(scene.place)
            )
            if self.place:
                old_name = (
                    self.place.name if hasattr(self.place, "name") else str(self.place)
                )
                if old_name != new_name:
                    self.atmosphere.clear()
                    self.lighting = None

            self.place = scene.place

        DECAY_RATE = 0.8
        toremove = []
        for tag in self.atmosphere_scores:
            self.atmosphere_scores[tag] *= DECAY_RATE
            if self.atmosphere_scores[tag] < 0.2:
                toremove.append(tag)

        for tag in toremove:
            del self.atmosphere_scores[tag]

        self.atmosphere = set(self.atmosphere_scores.keys())

        current_page_num = scene.page

        for char in scene.characters:
            if hasattr(char, "clothing") and char.clothing:
                top = char.clothing[0]
                self.last_known_clothing[char.name] = {
                    "desc": top["desc"],
                    "page": top["page"],
                }

        clothing_decay_window = 5
        expired_clothing = []
        if current_page_num:
            for name, info in self.last_known_clothing.items():
                if current_page_num - info["page"] > clothing_decay_window:
                    expired_clothing.append(name)

            for name in expired_clothing:
                del self.last_known_clothing[name]

        for ev in [scene.dominant_action, scene.dominant_state]:
            if ev and hasattr(ev, "type") and ev.type == "WEARS":
                if hasattr(ev.subject, "name") and hasattr(ev.object, "name"):
                    self.last_known_clothing[ev.subject.name] = {
                        "desc": ev.object.name,
                        "page": current_page_num if current_page_num else 0,
                    }

    def update_from_mood(self, mood):
        if mood.tone == "fear":
            self.lighting = "dim, cold light, long shadows"
        elif mood.tone == "sadness":
            self.lighting = "low light, muted tones, greycast"
        elif mood.tone == "calm":
            self.lighting = "soft, diffused light, peaceful"
        elif mood.tone == "joy":
            self.lighting = "warm, golden hour light, clear air"
        else:
            self.lighting = "neutral lighting"

    def update_from_atmosphere(self, atmosphere):
        if not atmosphere:
            return

        new_tags = set(atmosphere)
        toremove_antonyms = set()

        for existing in self.atmosphere_scores:
            if existing in self.ATMOSPHERE_ANTONYMS:
                antonyms = self.ATMOSPHERE_ANTONYMS[existing]
                if new_tags.intersection(antonyms):
                    toremove_antonyms.add(existing)

        for k in toremove_antonyms:
            if k in self.atmosphere_scores:
                del self.atmosphere_scores[k]

        for tag in new_tags:
            old_score = self.atmosphere_scores.get(tag, 0.0)

            boost = 1.0 if old_score == 0 else 0.4
            self.atmosphere_scores[tag] = min(2.0, old_score + boost)

        current_tags = set(self.atmosphere_scores.keys())
        if "storm" in current_tags:
            if "rain" in self.atmosphere_scores:
                del self.atmosphere_scores["rain"]
            if "drizzle" in self.atmosphere_scores:
                del self.atmosphere_scores["drizzle"]
        elif "rain" in current_tags:
            if "drizzle" in self.atmosphere_scores:
                del self.atmosphere_scores["drizzle"]

        current_tags = set(self.atmosphere_scores.keys())
        if "darkness" in current_tags:
            if "dim" in self.atmosphere_scores:
                del self.atmosphere_scores["dim"]
            if "shadow" in self.atmosphere_scores:
                del self.atmosphere_scores["shadow"]

        self.atmosphere = set([k for k, v in self.atmosphere_scores.items() if v > 0.3])


class ImageFrame:
    def __init__(
        self,
        page,
        characters,
        objects,
        place,
        dominant_action,
        dominant_state,
        mood,
        lighting,
        atmosphere,
        style,
        composition="",
        clothing_context=None,
        visual_evidence=None,
    ):
        self.page = page
        self.characters = characters
        self.objects = objects
        self.place = place
        self.dominant_action = dominant_action
        self.dominant_state = dominant_state
        self.mood = mood
        self.lighting = lighting
        self.atmosphere = atmosphere
        self.style = style
        self.composition = composition
        self.clothing_context = clothing_context or {}
        self.visual_evidence = visual_evidence or {}
        self.continuity = getattr(page, "continuity", None)
        self.intensity = 0.0

    def set_camera_stats(self, continuity, intensity):
        self.continuity = continuity
        self.intensity = intensity


class ImageFrameBuilder:

    GLOBAL_STYLE = (
        "watercolor illustration, hand-painted look, "
        "soft edges, muted color palette, cinematic lighting"
    )

    def __init__(self):
        self.world = VisualWorldState()

    def _derive_composition(self, scene_frame):
        parts = []

        if scene_frame.continuity == "enter":
            parts.append("Wide establishing shot")
        elif scene_frame.continuity == "transition":
            parts.append("Medium cinematic shot")
        elif scene_frame.continuity == "exit":
            parts.append("Wide fade shot")
        elif scene_frame.intensity > 0.6:
            parts.append("Close-up shot, shallow depth of field")
        elif len(scene_frame.characters) > 3:
            parts.append("Wide angle, crowd shot")
        elif len(scene_frame.characters) > 2:
            parts.append("Medium shot, wide angle")
        else:
            parts.append("Cinematic medium shot")

        if hasattr(scene_frame, "spatial_relations"):
            for subj, rel, obj in scene_frame.spatial_relations:
                s_name = subj.name
                o_name = obj.name

                if rel == "behind":
                    parts.append(f"foreground {o_name}, {s_name} in background")
                elif rel == "near" or rel == "by":
                    parts.append(f"{s_name} next to {o_name}")
                elif rel == "on":
                    parts.append(f"{s_name} positioned on {o_name}")
                elif rel == "under":
                    parts.append(f"low angle shot, {s_name} under {o_name}")

        return ", ".join(parts)

    def build(self, scene_frame, mood, atmosphere=None, visual_evidence=None):
        self.world.update_from_scene(scene_frame)
        self.world.update_from_mood(mood)
        self.world.update_from_atmosphere(atmosphere)

        visual_chars = [
            c for c in scene_frame.characters if getattr(c, "kind", "") != "ABSTRACT"
        ]
        visual_objs = [
            o for o in scene_frame.objects if getattr(o, "kind", "") != "ABSTRACT"
        ]

        current_atm = list(self.world.atmosphere)

        comp = self._derive_composition(scene_frame)

        frame = ImageFrame(
            page=scene_frame.page,
            characters=visual_chars,
            objects=visual_objs,
            place=self.world.place,
            dominant_action=scene_frame.dominant_action,
            dominant_state=scene_frame.dominant_state,
            mood=mood,
            lighting=self.world.lighting,
            atmosphere=current_atm,
            style=self.GLOBAL_STYLE,
            composition=comp,
            clothing_context={
                k: v["desc"] for k, v in self.world.last_known_clothing.items()
            },
            visual_evidence=visual_evidence,
        )
        if hasattr(scene_frame, "continuity"):
            frame.set_camera_stats(scene_frame.continuity, scene_frame.intensity)
        return frame


class PromptBuilder:

    RELATION_VERBS = RELATION_VERBS
    VISUAL_VERBS = VISUAL_VERBS
    ABSTRACT_MAP = ABSTRACT_MAP
    ATMOSPHERE_CLUSTERS = ATMOSPHERE_CLUSTERS
    ATM_PHRASES = ATM_PHRASES
    LIGHTING_TEMPLATES = LIGHTING_TEMPLATES

    def _to_gerund(self, lemma):
        if not lemma:
            return ""
        lemma = lemma.lower()

        irregulars = {
            "sit": "sitting",
            "run": "running",
            "step": "stepping",
            "stop": "stopping",
            "drop": "dropping",
            "put": "putting",
            "cut": "cutting",
            "get": "getting",
            "let": "letting",
            "set": "setting",
            "begin": "beginning",
            "dig": "digging",
            "swim": "swimming",
            "lie": "lying",
            "die": "dying",
            "tie": "tying",
            "freeze": "freezing",
        }
        if lemma in irregulars:
            return irregulars[lemma]

        if lemma.endswith("e") and not lemma.endswith("ee"):
            return lemma[:-1] + "ing"
        return lemma + "ing"

    def verbalize_event(self, ev):
        subj = getattr(ev.subject, "name", "")
        obj = getattr(ev.object, "name", "")

        phrase = subj

        SOFT_ACTIONS = {"freeze", "pause", "stop", "wait", "think"}
        lemma = ev.lemma.lower() if hasattr(ev, "lemma") else ""

        if lemma and lemma not in self.VISUAL_VERBS and lemma not in SOFT_ACTIONS:
            phrase = f"{subj}"
        elif lemma in SOFT_ACTIONS:
            phrase = f"{subj} standing still"
        elif lemma:
            phrase += f" {self._to_gerund(lemma)}"

        if obj:
            phrase += f" {obj.lower()}"

        return phrase

    def _resolve_lighting_conflicts(self, lights):
        if not lights:
            return []

        final = set(lights)
        NATURAL = {"sun", "sunny", "daylight", "morning", "noon"}
        if any(x in final for x in NATURAL):
            final.discard("lamp")
            final.discard("darkness")
            final.discard("dim")
            final.discard("gloom")

        return list(final)

    def _rank_descriptors(self, descriptors, limit=6):
        seen = set()
        unique = []
        for d in descriptors:
            if d not in seen:
                unique.append(d)
                seen.add(d)

        def score_desc(d):
            d_lower = d.lower()
            if any(
                w in d_lower
                for w in ["rain", "fog", "snow", "wind", "storm", "weather"]
            ):
                return 3
            if any(
                w in d_lower for w in ["light", "shadow", "glow", "lamp", "sun", "dark"]
            ):
                return 3
            if any(w in d_lower for w in ["style", "illustration"]):
                return 1
            return 2

        unique.sort(key=score_desc, reverse=True)
        return unique[:limit]

    def build(self, frame: ImageFrame) -> str:
        parts = []

        if frame.composition:
            parts.append(frame.composition)
        else:
            parts.append("Cinematic shot")

        candidates = list(frame.characters)

        def subject_score(char):
            score = 0
            if (
                frame.dominant_action
                and hasattr(frame.dominant_action, "subject")
                and frame.dominant_action.subject == char
            ):
                score += 10
            if (
                frame.dominant_state
                and hasattr(frame.dominant_state, "subject")
                and frame.dominant_state.subject == char
            ):
                score += 5
            if hasattr(char, "last_page") and char.last_page:
                score += char.last_page * 0.1
            return score

        candidates.sort(key=subject_score, reverse=True)

        subjects = [c.name for c in candidates][:2]

        scene_focus = ""

        if subjects:
            if frame.dominant_action:
                ev = frame.dominant_action
                if hasattr(ev, "lemma"):
                    scene_focus = self.verbalize_event(ev)
                elif hasattr(ev, "type"):
                    verb = self.RELATION_VERBS.get(ev.type, "featuring")
                    s_ent = getattr(ev, "subject", getattr(ev, "source", None))
                    o_ent = getattr(ev, "object", getattr(ev, "target", None))
                    subj = getattr(s_ent, "name", "Scene")
                    obj = getattr(o_ent, "name", "")
                    scene_focus = f"{subj} {verb} {obj}" if obj else f"{subj} {verb}"

            if not scene_focus:
                scene_focus = " and ".join(subjects)

            for char_obj in candidates[:2]:
                name = char_obj.name
                traits = []
                if hasattr(char_obj, "hair") and char_obj.hair:
                    traits.append(next(iter(char_obj.hair)))
                if name in frame.clothing_context:
                    traits.append(f"wearing {frame.clothing_context[name]}")
                elif hasattr(char_obj, "clothing") and char_obj.clothing:
                    traits.append(f"wearing {char_obj.clothing[0]['desc']}")

                if traits:
                    scene_focus = scene_focus.replace(
                        name, f"{name} ({', '.join(traits)})"
                    )

        else:
            if frame.objects:
                anchor_obj = frame.objects[0]
                scene_focus = f"focus on {anchor_obj.name}"
                if (
                    hasattr(anchor_obj, "attributes")
                    and "condition" in anchor_obj.attributes
                ):
                    conds = list(anchor_obj.attributes["condition"])
                    if conds:
                        scene_focus = f"focus on {conds[0]} {anchor_obj.name}"
            elif frame.place:
                scene_focus = f"empty {frame.place.name}"
            else:
                scene_focus = "empty cinematic environment"

        parts.append(scene_focus)

        if frame.place:
            parts.append(f"in {frame.place.name}")

        atms = []
        if frame.visual_evidence:
            if "weather" in frame.visual_evidence:
                atms.extend(frame.visual_evidence["weather"])
            if "conditions" in frame.visual_evidence:
                atms.extend(frame.visual_evidence["conditions"])
        if frame.atmosphere:
            atms.extend(frame.atmosphere)

        cluster_counts = {}
        raw_tags = []

        for t in atms:
            t_lower = t.lower()
            if t_lower in self.ABSTRACT_MAP:
                t_lower = self.ABSTRACT_MAP[t_lower]

            found_cluster = False
            for c_name, members in self.ATMOSPHERE_CLUSTERS.items():
                if t_lower in members or t_lower == c_name:
                    cluster_counts[c_name] = cluster_counts.get(c_name, 0) + 1
                    found_cluster = True
                    break

            raw_tags.append(t_lower)

        final_atms = []
        for c, count in cluster_counts.items():
            phrase = self.ATM_PHRASES.get(c, f"{c} atmosphere")
            final_atms.append(phrase)

        unique_raw = [
            x for x in self._rank_descriptors(raw_tags) if x not in cluster_counts
        ]
        final_atms.extend(unique_raw)

        final_atms = self._rank_descriptors(final_atms, limit=6)

        parts.append(", ".join(final_atms))
        lights = []
        has_evidence = False
        if frame.visual_evidence and "lighting" in frame.visual_evidence:
            lights.extend(frame.visual_evidence["lighting"])
            has_evidence = True

        if not has_evidence and frame.lighting:
            lights.append(str(frame.lighting))

        if lights:
            resolved = self._resolve_lighting_conflicts(lights)
            lighting_desc = ""
            resolved_set = set(resolved)

            for key_set, template in self.LIGHTING_TEMPLATES.items():
                if key_set.issubset(resolved_set):
                    lighting_desc = template
                    break

            if lighting_desc:
                parts.append(lighting_desc)
            else:
                parts.append(", ".join(resolved[:2]))

        parts.append(f"({frame.style}:1.2)")
        parts.append("masterpiece, best quality, 8k, highly detailed")

        return ", ".join([p for p in parts if p])
