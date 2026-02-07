from dataclasses import dataclass
from typing import Dict
import numpy as np
from core.constants import EMOTION_ANCHORS, ATMOSPHERE_ANCHORS


@dataclass(frozen=True)
class Mood:
    valence: float
    arousal: float
    tension: float
    tone: str


class MoodExtractor:

    EMOTION_ANCHORS = EMOTION_ANCHORS

    def __init__(self, embedder):
        self.embedder = embedder
        self.anchor_vecs = {
            label: embedder.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            for label, text in self.EMOTION_ANCHORS.items()
        }

        self.ATMOSPHERE_ANCHORS = ATMOSPHERE_ANCHORS

        self.atmosphere_vecs = {
            label: embedder.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            for label, text in self.ATMOSPHERE_ANCHORS.items()
        }

    def extract(self, page) -> Mood:
        vec = page.embedding

        scores = {
            label: float(np.dot(vec, anchor_vec))
            for label, anchor_vec in self.anchor_vecs.items()
        }

        valence = scores["joy"] - scores["sadness"]
        arousal = max(scores["fear"], scores["anger"])
        tension = scores["fear"]

        tone = max(scores, key=scores.get)

        return Mood(
            valence=round(self._clamp(valence), 2),
            arousal=round(self._clamp(arousal), 2),
            tension=round(self._clamp(tension), 2),
            tone=tone,
        )

    def extract_atmosphere(self, page):
        if not page.sentences:
            return []
        texts = [s["text"] for s in page.sentences]
        sent_vecs = self.embedder.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        )

        scores = {}
        for label, anchor_vec in self.atmosphere_vecs.items():
            sims = np.dot(sent_vecs, anchor_vec)

            k = min(3, len(sims))
            if k > 0:
                top_k = np.partition(sims, -k)[-k:]
                scores[label] = float(np.mean(top_k))
            else:
                scores[label] = 0.0

        all_vals = list(scores.values())
        if not all_vals:
            return []

        noise_floor = np.mean(all_vals)
        adaptive_thresh = noise_floor + 0.1

        final_thresh = max(0.20, adaptive_thresh)

        active = [(atm, score) for atm, score in scores.items() if score > final_thresh]
        active.sort(key=lambda x: x[1], reverse=True)

        return [x[0] for x in active[:3]]

    def _clamp(self, x: float) -> float:
        return max(-1.0, min(1.0, x))
