from core.engine import NLPEngine

engine = NLPEngine()

text = """Nairi had not planned to return to the valley.
The valley had once been her home.
She remembered the river clearly.
When she saw it again, Nairi felt something break inside her.
she used to live in a broken house.
"""

page = engine.analyze(1, text)

print("\nSENTENCES:", len(page.sentences))
print("ENTITIES:", page.doc.ents)
print("COREF:", page.doc._.coref_clusters)
print("COREF Page:", page.coref_clusters)
for cluster in page.doc._.coref_clusters:
    print("Cluster:", cluster)
    print("Mentions:", [text[start:end] for (start,end) in cluster])
print("COREF:", page.doc._.resolved_text)
print("CHARACTERS:", page.characters.keys())
print("LOCATIONS:", page.locations.keys())
print("EMBEDDING SHAPE:", len(page.embedding))
print("World Entities:", page.world_ents)
print("Noun Entities:", page.noun_ents)