import nltk
from collections import defaultdict

SCORE_NOUN_MATCH = 5.0      
SCORE_VERB_AGENT = 2.0     
SCORE_VERB_MOTION = 1.0 
SCORE_FALLBACK = 0.1   


TYPE_HIERARCHY = {
    "unknown": 0,
    "ABSTRACT": 1,
    "OBJECT": 2,
    "PLACE": 3,    
    "CHARACTER": 4  
}

AGENTIVE_DOMAINS = {
    "verb.cognition", "verb.communication", "verb.emotion",
    "verb.perception", "verb.social", "verb.competition",
    "verb.consumption", "verb.body",
}

class Typer:
    def __init__(self):
        print("Loading Evidence-Based Typing Engine...")
        try:
            nltk.data.find("corpora/wordnet.zip")
        except LookupError:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
        from nltk.corpus import wordnet
        self.wn = wordnet

    def infer_and_lock(self, entity, world):
     
        if not hasattr(entity, "type_scores"):
            entity.type_scores = defaultdict(float)
            entity.locked = False

        if getattr(entity, "locked", False):
            return entity.kind

        self._score_noun_semantics(entity)

        self._score_verb_semantics(entity, world)


        if not entity.type_scores:
            entity.kind = "ABSTRACT"
            return entity.kind

            
        best_type = max(entity.type_scores, key=entity.type_scores.get)
        current_type = entity.kind

        
        curr_level = TYPE_HIERARCHY.get(current_type, 0)
        new_level = TYPE_HIERARCHY.get(best_type, 0)

        if best_type == "CHARACTER":
            head = entity.name.split()[-1].lower()
            synsets = self.wn.synsets(head)
            if synsets:
                lex = synsets[0].lexname()
                if any(x in lex for x in ("artifact", "location", "structure")):
                    best_type = "PLACE" if "location" in lex else "OBJECT"

        if new_level >= curr_level:
            entity.kind = best_type
        else:
            entity.kind = current_type

        return entity.kind

    def finalize(self, entity):
        entity.locked = True


    def _score_noun_semantics(self, entity):
        head = entity.name.split()[-1].lower()
        synsets = self.wn.synsets(head)
        if not synsets:
            return

        primary = synsets[0]
        lex = primary.lexname()

        if "time" in lex or "cognition" in lex:
            entity.type_scores["ABSTRACT"] += SCORE_NOUN_MATCH
            return  

        if "person" in lex or "animal" in lex:
            entity.type_scores["CHARACTER"] += SCORE_NOUN_MATCH

        elif "location" in lex:
            entity.type_scores["PLACE"] += SCORE_NOUN_MATCH

        elif "group" in lex:
            entity.type_scores["CHARACTER"] += SCORE_NOUN_MATCH * 0.5

        elif "artifact" in lex or "object" in lex:
            entity.type_scores["OBJECT"] += SCORE_NOUN_MATCH

        if primary.hypernym_paths():
            hypers = {
                h.name()
                for path in primary.hypernym_paths()
                for h in path
            }
            if "location.n.01" in hypers:
                entity.type_scores["PLACE"] += SCORE_NOUN_MATCH


    def _score_verb_semantics(self, entity, world):

        for ev in world.events:
            if ev.subject != entity: continue
            if entity.type_scores["OBJECT"] < 1.0:
                entity.type_scores["OBJECT"] += SCORE_FALLBACK

            synsets = self.wn.synsets(ev.lemma.lower(), pos=self.wn.VERB)
            if not synsets: continue
            
            domain = synsets[0].lexname()

            if domain == "verb.perception" and ev.object is None:
                continue

            if domain in AGENTIVE_DOMAINS:
                entity.type_scores["CHARACTER"] += SCORE_VERB_AGENT
            
            elif domain == "verb.motion":
                if self.is_intentional_agent(entity) and entity.kind not in ("PLACE",):
                    entity.type_scores["CHARACTER"] += SCORE_VERB_MOTION

    
    def is_intentional_agent(self,entity):
        head = entity.name.split()[-1].lower()
        synsets = self.wn.synsets(head)
        if not synsets:
            return False

        lex = synsets[0].lexname()
        return "person" in lex or "animal" in lex
