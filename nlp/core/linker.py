
def resolve(node, page, world):
    if node is None:
        return None

    if hasattr(node, "text") and hasattr(node, "pos_"):
        text = node.text.lower()
        head = node.lemma_.lower()
    elif hasattr(node, "root"):
        text = node.text.lower()
        head = node.root.lemma_.lower()
    else:
        return None

   
    for ent in world.ents.values():
        
        if text in ent.aliases or head in ent.aliases:
            return ent
            
        for alias in ent.aliases:
            alias_parts = alias.split()
            if head in alias_parts:
                return ent

    return {
        "text": node.text,
        "lemma": head,
        "pos": node.pos_ if hasattr(node, "pos_") else None,
    }