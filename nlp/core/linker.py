def resolve(node, mention_map):
    if node is None:
        return None

    if hasattr(node, "id"):
        return node
    
    node_start = node.idx
    node_end = node.idx + len(node.text)

    for (start, end), ent in mention_map.items():
        if start <= node_start and end >= node_end:
            return ent
        
    return {
        "text": node.text,
        "lemma": node.lemma_,
        "pos": node.pos_
    }