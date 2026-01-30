import numpy as np
from collections import defaultdict

PRONOUNS = {
    "i","me","we","us","you","he","him","she","her","it","they","them",
    "mine","ours","yours","his","hers","theirs","its","their",
    "myself","ourselves","yourself","yourselves","himself","herself",
    "itself","themselves","oneself",
    "this","that","these","those","such","one","ones",
    "each","either","neither","every","none",
    "who","whom","whose","which","that",
    "each other","one another",
    "everybody","somebody","nobody","anybody","someone","no one","anyone",
    "everything","something","nothing","anything",
    "all","some","any","both","another","much","few","little",
}

def is_pronoun(text: str) -> bool:
    return " ".join(text.lower().split()) in PRONOUNS

class Entity:
    def __init__(self, eid, name, kind="unknown", embedding=None):
        self.id = eid
        self.name = name
        self.kind = kind

        self.aliases = set([name.lower()])
        self.mentions = []

        self.first_page = None
        self.last_page = None

        self.embeddings = []
        self.attributes = defaultdict(list)
        self.relations = defaultdict(set)

        if embedding is not None:
            self.embeddings.append(embedding)

    # -------------------------------------------------------------------------

    def update(self, mention, page_num, embedding=None):
        self.mentions.append(mention)

        text = mention["text"].lower()
        if not is_pronoun(text):
            self.aliases.add(text)

        if self.first_page is None:
            self.first_page = page_num
        self.last_page = page_num

        if embedding is not None:
            self.embeddings.append(embedding)

    # -------------------------------------------------------------------------

    def mean_emb(self):
        if not self.embeddings:
            return None
        return np.mean(np.vstack(self.embeddings), axis=0)

    # -------------------------------------------------------------------------

    def about(self):
        return (
            f"Entity:{self.name} | Kind:{self.kind} | "
            f"Pages:{self.first_page}-{self.last_page}"
        )
