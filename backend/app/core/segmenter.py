import spacy
from core.objects import Scene

sp = spacy.load("en_core_web_sm")


def extract_sentences(pages):
    sentences = []
    char_ind = 0

    for page in pages:
        page_num = page["page"]
        text = page["text"]
        doc = sp(text)

        for sent in doc.sents:
            s = sent.text.strip()
            if not s:
                continue

            sentences.append(
                {
                    "text": s,
                    "page": page_num,
                    "char_st": char_ind,
                    "char_en": char_ind + len(s),
                }
            )
            char_ind += len(s) + 1
    return sentences


def get_scenes(pages):
    sentences =extract_sentences(pages)
    scenes, buffer = [], []
    buffer_len = 0
    scene_id = 1

    for sent in sentences:
        if not buffer:
            scene_st_page = sent["page"]
            scene_st_char = sent["char_st"]
        buffer.append(sent)
        buffer_len += len(sent["text"])

        scene_en_page = sent["page"]
        scene_en_char = sent["char_en"]

        if buffer_len >= 1400:
            text = " ".join(s["text"] for s in buffer)
            scenes.append(
                Scene(
                    scene_id=scene_id,
                    text=text,
                    start_page=scene_st_page,
                    end_page=scene_en_page,
                    char_start=scene_st_char,
                    char_end=scene_en_char,
                )
            )

            scene_id += 1
            buffer = []
            buffer_len = 0

    if buffer:
        text = " ".join(s["text"] for s in buffer)
        scenes.append(
            Scene(
                scene_id=scene_id,
                text=text,
                start_page=scene_st_page,
                end_page=scene_en_page,
                char_start=scene_st_char,
                char_end=scene_en_char,
            )
        )

    return scenes