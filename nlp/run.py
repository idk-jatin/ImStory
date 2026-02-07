# import os
# import gc
# import logging
# import warnings

# import torch
# import tqdm
# from transformers import logging as hf_logging

# os.environ["TOKENIZERS_PARALLELISM"] = "false"
# os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
# os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

# hf_logging.set_verbosity_error()
# logging.basicConfig(level=logging.ERROR)

# for lib in (
#     "transformers",
#     "sentence_transformers",
#     "torch",
#     "thinc",
#     "spacy",
#     "urllib3",
# ):
#     logging.getLogger(lib).setLevel(logging.ERROR)

# tqdm.tqdm.disable = True
# warnings.filterwarnings("ignore", category=FutureWarning)


# from core.engine import NLPEngine
# from core.memory import World
# from core.typing import Typer
# from core.relationship import RelationExtractor
# from core.promoter import Promoter


# # PAGES = [

# # """
# # Nairi arrived at the valley just before sunset.
# # The hills stood silent on either side.
# # The air felt heavy, as if holding old memories.
# # She paused at the edge of the path.
# # Something about the place felt familiar.
# # """,

# # """
# # She walked slowly toward the river.
# # The water reflected the fading orange sky.
# # Nairi tightened her grip on the old lantern.
# # Its light flickered against the stones.
# # The valley remained unnaturally quiet.
# # """,

# # """
# # The path narrowed as it curved downhill.
# # Tall grass brushed against her legs.
# # The sound of flowing water grew louder.
# # Nairi glanced back once.
# # No one followed her.
# # """,

# # """
# # A broken house stood near the riverbank.
# # Its roof sagged under years of neglect.
# # The windows were dark and empty.
# # Nairi stopped a few steps away.
# # She felt watched.
# # """,

# # """
# # The house loomed larger as she approached.
# # Loose boards creaked beneath the wind.
# # The lantern’s glow revealed cracked walls.
# # Nairi swallowed and stepped closer.
# # Her unease deepened.
# # """,

# # """
# # A faint movement came from inside the house.
# # The shadows shifted near the doorway.
# # Nairi raised the lantern higher.
# # Her heart began to race.
# # She held her breath.
# # """,

# # """
# # An old man emerged from the darkness.
# # His face was lined and unreadable.
# # He stood silently near the door.
# # Nairi froze in place.
# # The lantern trembled in her hand.
# # """,

# # """
# # The old man watched her carefully.
# # His eyes reflected the lantern light.
# # Neither of them spoke.
# # The river flowed softly behind them.
# # The moment stretched.
# # """,

# # """
# # Nairi shifted her weight nervously.
# # The old man did not move.
# # The house creaked behind him.
# # The silence felt deliberate.
# # Nairi waited.
# # """,

# # """
# # At last, the old man spoke.
# # His voice was calm and steady.
# # He said the valley had changed.
# # Nairi frowned at his words.
# # The lantern flickered again.
# # """,

# # """
# # The old man stepped closer.
# # He introduced himself as Ardan.
# # His gaze never left Nairi.
# # The name sounded familiar to her.
# # She felt a knot form in her chest.
# # """,

# # """
# # Ardan spoke of the land and the river.
# # He said time had reshaped everything.
# # Nairi shook her head in disbelief.
# # Her voice rose as she argued.
# # The wind stirred around them.
# # """,

# # """
# # Ardan remained calm despite her anger.
# # He pointed toward the riverbank.
# # The water moved steadily beside them.
# # Nairi followed his gesture.
# # Her anger slowly gave way to doubt.
# # """,

# # """
# # The lantern slipped in Nairi’s grasp.
# # It fell to the ground with a dull sound.
# # The light dimmed but did not go out.
# # Both of them looked down.
# # No one spoke.
# # """,

# # """
# # The broken house stood silently behind them.
# # The river continued its endless flow.
# # Ardan turned away from Nairi.
# # His figure moved toward the water.
# # The distance between them grew.
# # """,

# # """
# # Nairi watched Ardan walk away.
# # The lantern lay near her feet.
# # The night air felt colder now.
# # She remained beside the house.
# # Alone.
# # """,

# # """
# # The wind carried faint sounds from the valley.
# # The house creaked softly in the darkness.
# # Nairi picked up the lantern.
# # Its light steadied once more.
# # She exhaled slowly.
# # """,

# # """
# # She looked toward the river again.
# # Ardan was no longer visible.
# # The water reflected the moonlight.
# # The valley seemed unchanged.
# # Yet everything felt different.
# # """,

# # """
# # Nairi turned away from the river.
# # The broken house faded behind her.
# # The path ahead stretched into darkness.
# # She held the lantern close.
# # And walked on.
# # """,

# # """
# # The valley settled into silence.
# # The river flowed unseen in the dark.
# # The house stood empty once more.
# # Nairi’s footsteps disappeared down the path.
# # The night reclaimed everything.
# # """
# # ]
# PAGES = [

# # PAGE 1
# """
# Arjun arrived in the coastal town just before dusk.
# The bus left behind a cloud of dust.
# A small suitcase rested in his hand.
# Wind carried the smell of salt.
# The harbor lay ahead, unusually quiet.
# Fishing boats rocked gently.
# Clouds gathered slowly overhead.
# A flickering lamp stood near the pier entrance.
# Water reflected broken light patterns.
# A distant bell rang once.
# No people remained outside.
# Shutters closed across nearby shops.
# The tide crept closer to the stones.
# Arjun adjusted his jacket collar.
# He looked toward the sea for a long moment.
# Rain began as a light drizzle.
# Footsteps echoed faintly on wood.
# A torn poster fluttered nearby.
# Someone had written a date on it.
# The ink had partly washed away.
# Arjun took out an old photograph.
# He stared at it silently.
# The harbor wind strengthened.
# Fog started forming over the water.
# Evening settled quickly.
# The first streetlight switched on.
# Arjun walked toward the pier.
# The photograph returned to his pocket.
# The drizzle continued steadily.
# Night approached without color.
# """,

# # PAGE 2
# """
# Rain intensified within minutes.
# Drops struck the pier rhythmically.
# Arjun stopped beneath the harbor lamp.
# Light revealed tired eyes.
# Water dripped from his hair.
# The photograph edge showed again.
# It depicted two young men beside a boat.
# One of them resembled Arjun.
# The other face remained partly faded.
# Thunder sounded far offshore.
# Fog thickened along the horizon.
# A lone gull crossed overhead.
# Wind tugged at Arjun’s coat.
# A small boat rope snapped against wood.
# Water splashed onto his shoes.
# The town lights dimmed behind him.
# The sea appeared darker than before.
# Arjun whispered something quietly.
# The rain drowned the words.
# He stepped further onto the pier.
# The lamp hummed softly.
# Reflections danced on puddles.
# A buoy clanged repeatedly.
# The photograph slipped briefly.
# Arjun caught it quickly.
# His grip tightened afterward.
# The fog swallowed distant boats.
# The harbor became a blur.
# Rain showed no sign of stopping.
# """,

# # PAGE 3
# """
# Morning arrived without sunlight.
# Clouds covered the sky completely.
# Rain reduced to mist.
# Arjun remained near the end of the pier.
# A thermos sat beside him.
# Steam rose faintly from its lid.
# Fishing nets lay abandoned nearby.
# Wood creaked under shifting tide pressure.
# The photograph rested in his hand again.
# He studied it more carefully now.
# A name appeared on the back.
# The ink had smudged but remained readable.
# Arjun traced it with his finger.
# A memory seemed to surface.
# His posture changed slightly.
# Wind blew colder than before.
# The gull returned briefly.
# It landed near the thermos.
# Then it flew off again.
# A distant engine started somewhere.
# The town slowly woke behind him.
# Doors opened along the harbor street.
# Muted voices carried through fog.
# Arjun finally stood up.
# He placed the photograph carefully inside the suitcase.
# Mist followed him as he walked back.
# The harbor looked unchanged.
# But Arjun’s expression had shifted.
# Determination replaced hesitation.
# """,

# # PAGE 4
# """
# Arjun walked toward an old warehouse.
# Its paint had faded years ago.
# Rust marked the metal shutters.
# A signboard hung crooked above the door.
# Rainwater dripped steadily from its edge.
# The building faced the harbor directly.
# Arjun paused before entering.
# He wiped moisture from the photograph again.
# Inside, light came through broken panels.
# Dust floated in thin beams.
# An empty chair stood near a table.
# Boot prints marked the floor.
# Someone had visited recently.
# Arjun examined the surroundings quietly.
# A notebook lay partly hidden.
# Its pages showed recent entries.
# Dates matched the poster outside.
# A realization crossed his face.
# The second man from the photograph might be here.
# Wind pushed the door slightly.
# It creaked loudly.
# Arjun closed it firmly.
# Silence filled the warehouse again.
# Outside, fog began lifting.
# Faint sunlight struggled through clouds.
# Time seemed to be moving forward again.
# """,

# # PAGE 5
# """
# Late afternoon brought clearer skies.
# Rain finally stopped completely.
# Sunlight reflected off wet harbor stones.
# Arjun stood outside the warehouse.
# The notebook rested in his hand.
# Footsteps approached from the pier.
# Another figure emerged slowly.
# The man looked older but familiar.
# Recognition appeared instantly.
# Neither spoke at first.
# The sea sounded calmer now.
# Gulls circled overhead.
# Clouds broke apart gradually.
# Light warmed both faces.
# The photograph matched reality again.
# Years of distance seemed to shrink.
# The second man extended a hand.
# Arjun accepted it quietly.
# Relief replaced tension.
# The harbor no longer felt silent.
# Voices returned to the street.
# Boats resumed movement.
# Water sparkled under sunlight.
# A new chapter had clearly begun.
# The photograph stayed safely inside the suitcase.
# This time, it no longer felt unfinished.
# """

# ]





# # PAGES = [
# #     """
# #     Nairi arrived at the valley just before sunset.
# #     The place felt quiet and abandoned.
# #     She carried an old lantern in her hand.
# #     The light from it flickered as she walked.
# #     """,

# #     """
# #     The valley stretched wide beneath the hills.
# #     Nairi followed a narrow path toward the river.
# #     The river reflected the fading sky.
# #     She remembered playing near it as a child.
# #     """,

# #     """
# #     A broken house stood near the riverbank.
# #     The house looked empty, but something inside watched her.
# #     Nairi slowed her steps and raised the lantern.
# #     She felt uneasy as she approached it.
# #     """,

# #     """
# #     An old man emerged from the shadows of the house.
# #     He watched Nairi silently.
# #     The lantern trembled in her grip.
# #     She sensed that he had been waiting for her.
# #     """,

# #     """
# #     The old man finally spoke.
# #     His name was Ardan.
# #     He told Nairi that the valley no longer belonged to her family.
# #     The words unsettled her.
# #     """,

# #     """
# #     Ardan pointed toward the river and then to the house.
# #     He said the land had changed over time.
# #     Nairi argued with him, but he remained calm.
# #     The lantern fell from her hand onto the ground.
# #     """,

# #     """
# #     The river flowed quietly beside the broken house.
# #     Ardan stood near it, watching the water.
# #     Nairi stared at the house in silence.
# #     She realized that some memories could never be reclaimed.
# #     """
# # ]

# # ---------------------------------------------------------
# # PHASE 1 — NLP + WORLD MEMORY
# # ---------------------------------------------------------
# print("\n--- [PHASE 1] LOADING EXTRACTION ENGINE ---")
# engine = NLPEngine()
# memory = World()

# print("\n--- PROCESSING PAGES ---")

# for idx, text in enumerate(PAGES, start=1):
#     print("\n" + "=" * 60)
#     print(f" PAGE {idx}")
#     print("=" * 60)
#     print(text.strip())

#     page = engine.analyze(idx, text)
#     memory.r_page(page)

#     print("\n World Entities:")
#     for ent in memory.ents.values():
#         print(f"  • {ent.about()}")
#         if ent.aliases:
#             print(f"      aliases: {sorted(ent.aliases)}")

#     print("\n Events:")
#     if page.events:
#         for ev in page.events:
#             print(f"  • {ev.lemma} | {ev.subject} → {ev.object} @ {ev.location}")
#     else:
#         print("  (none)")

#     print("\n Active Context (last 3 pages):")
#     for ent in memory.context():
#         print(f"  • {ent.name}")

# print("\n" + "=" * 60)

# # ---------------------------------------------------------
# # CLEAN GPU (IMPORTANT FOR LONG STORIES)
# # ---------------------------------------------------------
# print("\n--- FREEING GPU MEMORY ---")
# mood_engine = engine.mood_engine
# engine.nlp = None
# engine.embedder = None
# del engine
# gc.collect()
# torch.cuda.empty_cache()
# print("GPU Memory Cleared.")

# # ---------------------------------------------------------
# # PHASE 2 — ENTITY TYPING (ONCE, MONOTONIC)
# # ---------------------------------------------------------
# print("\n--- [PHASE 2] LOADING TYPING ENGINE ---")
# typer = Typer()
# memory.freeze_types(typer)

# # ---------------------------------------------------------
# # PHASE 3 — RELATIONSHIP EXTRACTION & PROMOTION
# # ---------------------------------------------------------
# print("\n--- [PHASE 3] RELATIONSHIP EXTRACTION & PROMOTION ---")

# rel_engine = RelationExtractor()
# raw_relations = rel_engine.process(memory)

# promoter = Promoter()
# story_facts = promoter.promote(raw_relations)

# promoter.print_graph(story_facts)

# # Persist if needed
# memory.relations = story_facts


# from core.salience import Salience
# from core.scene import SceneFrameBuilder

# salience_engine = Salience()
# frame_builder = SceneFrameBuilder()

# scene_frames = []
# prev_frame = None

# print("\n--- PAGE SALIENCE TRACE ---")
# # BUG 4 FIX: Stable Iteration Order
# for pnum, page in sorted(memory.pages.items()):
#     sal = salience_engine.compute(page, memory)
#     frame = frame_builder.build(page, sal, memory, prev_frame=prev_frame)

#     scene_frames.append(frame)

#     print("\nPAGE", pnum)
#     print(" Focus Entities:", [e.name for e in frame.primary_entities])

#     if frame.dominant_action:
#         ev = frame.dominant_action
#         if hasattr(ev, "lemma"):
#             subj = getattr(ev.subject, "name", ev.subject)
#             obj = getattr(ev.object, "name", ev.object)
#             loc = getattr(ev.location, "name", ev.location)

#             print(
#                 " Action:",
#                 f"{ev.lemma} | {subj} -> {obj} @ {loc}"
#             )
#         elif hasattr(ev, "type") and hasattr(ev, "source") and hasattr(ev, "target"):
#             print(
#                 " Action:",
#                 f"{ev.type} | {ev.source.name} -> {ev.target.name}"
#             )

#     if frame.dominant_state:
#         print(" State:", frame.dominant_state.type)

#     print(" Continuity:", frame.continuity)
#     print(" Intensity:", round(frame.intensity, 2))
#     print(" Visualizable:", frame.visualizable)
#     prev_frame = frame



# from core.image import ImageFrameBuilder, PromptBuilder


# image_builder = ImageFrameBuilder()
# prompt_builder = PromptBuilder()

# print("\n--- IMAGE PROMPTS ---")

# for frame in scene_frames:
#     page = memory.pages[frame.page]

#     mood = mood_engine.extract(page)
#     image_frame = image_builder.build(frame, mood, atmosphere=page.atmosphere, visual_evidence=page.visual_evidence)

#     prompt = prompt_builder.build(image_frame)

#     print(f"\nPAGE {frame.page}")
#     print(prompt)
#     print(f"Stats: Intensity={image_frame.intensity:.2f} | Continuity={image_frame.continuity} | Atmospheres={len(image_frame.atmosphere)}")


# print("\n--- FINAL MEMORY STATE ---")
# for ent in memory.ents.values():
#     if ent.kind != "ABSTRACT":
#         print(ent.about())

# if memory.relations:
#     print("\n--- FINAL RELATIONS ---")
#     for r in memory.relations:
#         print(
#             f"{r.source.name} --{r.type}--> {r.target.name} "
#             f"(pages {r.start_page}-{r.end_page} | conf={r.confidence})"
#         )

# print("\n✅ RUN COMPLETE — SYSTEM STABLE")
