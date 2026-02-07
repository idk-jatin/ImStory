import nltk


class RelationExtractor:
    def __init__(self):
        try:
            nltk.data.find("corpora/wordnet.zip")
        except LookupError:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
        from nltk.corpus import wordnet as wn

        self.wn = wn

    def process(self, memory):
        relationships = []
        for ev in memory.events:
            if not ev.object or not ev.subject:
                continue

            source = ev.subject
            target = ev.object

            if not hasattr(source, "id") or not hasattr(target, "id"):
                continue
            if source.id == target.id:
                continue

            rel_type = self._classify_relationship(ev.lemma)
            if not rel_type:
                continue

            valid, final_src, final_tgt = self._enforce_contract(
                rel_type, source, target
            )

            if valid:
                relationships.append(
                    {
                        "source": final_src.name,
                        "source_id": final_src.id,
                        "source_obj": final_src,
                        "type": rel_type,
                        "verb": ev.lemma,
                        "target": final_tgt.name,
                        "target_id": final_tgt.id,
                        "target_obj": final_tgt,
                        "sentence": ev.sentence,
                        "page": ev.page,
                    }
                )

        return relationships

    def _enforce_contract(self, rel_type, source, target):
        s_kind = source.kind
        t_kind = target.kind

        if rel_type == "POSSESSES":
            if s_kind == "OBJECT" and t_kind == "CHARACTER":
                return True, target, source

            if s_kind == "CHARACTER":
                return True, source, target

            return True, source, target

        if rel_type in ["OBSERVES", "FEELS", "INTERACTS"]:

            if s_kind == "OBJECT":
                return False, source, target

            return True, source, target

        if rel_type == "IS":
            return True, source, target

        return True, source, target

    def _classify_relationship(self, verb_lemma):
        synsets = self.wn.synsets(verb_lemma.lower(), pos=self.wn.VERB)
        if not synsets:
            return None

        primary = synsets[0]
        lex_domain = primary.lexname()

        if lex_domain == "verb.possession":
            return "POSSESSES"
        if self._is_hyponym_of(primary, ["possess.v.01", "have.v.01", "get.v.01"]):
            return "POSSESSES"

        if verb_lemma in {"be", "become", "remain"}:
            return "IS"

        if lex_domain == "verb.emotion":
            return "FEELS"

        if lex_domain in ["verb.social", "verb.communication"]:
            return "INTERACTS"

        if lex_domain == "verb.perception":
            return "OBSERVES"

        return None

    def _is_hyponym_of(self, synset, targets):
        queue = [synset]
        visited = set()
        while queue:
            current = queue.pop(0)
            if current.name() in visited:
                continue
            visited.add(current.name())
            if current.name() in targets:
                return True
            queue.extend(current.hypernyms())
        return False

    def print_graph(self, relationships):
        print("\n--- STORY RELATION GRAPH ---")
        if not relationships:
            print("(No persistent relationships found)")
            return

        print(f"{'SOURCE':<15} | {'RELATION':<14} | {'TARGET':<15}")
        print("-" * 48)
        for r in relationships:
            print(f"{r['source']:<15} | {r['type']:<14} | {r['target']:<15}")
