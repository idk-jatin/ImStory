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
    page = engine.analyze(i, text)
    memory.r_page(page)