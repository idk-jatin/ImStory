def resolve(node, page, world):
    if node is None:
        return None

    if hasattr(node, "text") and hasattr(node, "lemma_"):
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

    return {
        "text": node.text,
        "lemma": head,
        "pos": getattr(node, "pos_", None),
    }
