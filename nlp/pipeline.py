
import os
import gc
import logging
import warnings
import torch
from transformers import logging as hf_logging

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
hf_logging.set_verbosity_error()
logging.basicConfig(level=logging.ERROR)
for lib in ("transformers", "sentence_transformers", "torch", "thinc", "spacy", "urllib3"):
    logging.getLogger(lib).setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=FutureWarning)

from core.engine import NLPEngine
from core.memory import World
from core.typing import Typer
from core.relationship import RelationExtractor
from core.promoter import Promoter
from core.salience import Salience
from core.scene import SceneFrameBuilder
from core.image import ImageFrameBuilder, PromptBuilder

class StoryPipeline:
    def __init__(self):
        print("Initializing NLP Engine...")
        self.engine = NLPEngine()
        self.typer = Typer()
        self.rel_engine = RelationExtractor()
        self.promoter = Promoter()
        self.salience_engine = Salience()
        self.frame_builder = SceneFrameBuilder()
        self.image_builder = ImageFrameBuilder()
        self.prompt_builder = PromptBuilder()

    def process(self, pages_text: list[str]) -> list[dict]:
        memory = World()
        processed_pages = []

        for idx, text in enumerate(pages_text, start=1):
            if not text.strip(): continue
            page = self.engine.analyze(idx, text)
            memory.r_page(page)

        memory.freeze_types(self.typer)
        
        raw_relations = self.rel_engine.process(memory)
        story_facts = self.promoter.promote(raw_relations)
        memory.relations = story_facts


        scene_frames = []
        prev_frame = None
        for pnum, page in sorted(memory.pages.items()):
            sal = self.salience_engine.compute(page, memory)
            frame = self.frame_builder.build(page, sal, memory, prev_frame=prev_frame)
            scene_frames.append(frame)
            prev_frame = frame

        results = []
        for frame in scene_frames:
            page = memory.pages[frame.page]
            mood = self.engine.mood_engine.extract(page)
            
            image_frame = self.image_builder.build(
                frame, 
                mood, 
                atmosphere=page.atmosphere, 
                visual_evidence=page.visual_evidence
            )

            prompt = self.prompt_builder.build(image_frame)
            
            results.append({
                "page": frame.page,
                "text": page.text,
                "prompt": prompt,
                "stats": {
                    "intensity": float(image_frame.intensity),
                    "continuity": image_frame.continuity,
                    "atmosphere_count": len(image_frame.atmosphere)
                }
            })
            
        return results

    def cleanup(self):
        import torch, gc
        
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        pass
