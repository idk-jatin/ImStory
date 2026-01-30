import os
import warnings
import logging
import tqdm
from transformers import logging as hf_logging
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"


hf_logging.set_verbosity_error()

logging.basicConfig(level=logging.ERROR)
for name in [
    "transformers",
    "sentence_transformers",
    "torch",
    "thinc",
    "spacy",
    "urllib3",
]:
    logging.getLogger(name).setLevel(logging.ERROR)
tqdm.tqdm.disable = True
warnings.filterwarnings("ignore", category=FutureWarning)


from core.engine import NLPEngine
from core.memory import World

engine = NLPEngine()
memory = World()

pages = [
    """
    Nairi had not planned to return to the valley.
    She remembered the river clearly.
    It had once been her home.
    """,
    """
    The valley was silent.
    Nairi walked toward the river.
    The broken house stood nearby.
    She felt drawn to it.
    """,
    """
    An old man was sitting near the broken house.
    He watched her quietly.
    Nairi did not recognize him, but she felt she had seen him before.
    """,
    """
    The old man finally spoke.
    His name was Ardan.
    He told Nairi that the valley had changed.
    """,
    """
    Ardan pointed to the river and to the house.
    He said it no longer belonged to her family.
    The memory of it still hurt her.
    """,
    """
    The river flowed slowly through the valley.
    It carried reflections of the broken house.
    Nairi stood beside it in silence.
    """
]

for i, text in enumerate(pages, 1):
    print(f"\n{'='*60}")
    print(f" PAGE {i}")
    print(f"{'='*60}")
    print(text.strip())

    page = engine.analyze(i, text)
    memory.r_page(page)

    print("\n World Entities:")
    for ent in memory.ents.values():
        print(f"  • {ent.about()}")
        if ent.aliases:
            print(f"      aliases: {sorted(ent.aliases)}")

    if page.events:
        print("\n Events:")
        for ev in page.events:
            print(
                f"  • {ev.lemma} | "
                f"{ev.subject} → {ev.object} "
                f"@ {ev.location}"
            )
    else:
        print("\n Events: none")

    ctx = memory.context()
    print("\n Active Context (last 3 pages):")
    for ent in ctx:
        print(f"  • {ent.name}")

print(f"\n{'='*60}")
