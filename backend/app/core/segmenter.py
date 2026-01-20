def segment_scenes(pages):
    scenes =[]
    buffer=""
    scene_id = 1

    for p in pages:
        buffer +="\n" + p["text"]
        if len(buffer) > 1400:
            scenes.append({"id":scene_id,"text":buffer.strip()})
            scene_id+=1
            buffer=""
    if buffer.strip():
        scenes.append({"id":scene_id,"text":buffer.strip()})
    return scenes           