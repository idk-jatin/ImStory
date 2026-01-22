import spacy
from core.objects import Scene
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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


def get_similarity(buffer,next_sent, vz):
    texts = [s["text"] for s in buffer] + [next_sent["text"]]
    X = vz.transform(texts)
    context_vec = np.asarray(X[:-1].mean(axis=0))
    next_vec = X[-1]
    score = cosine_similarity(context_vec,next_vec)[0][0]
    return float(score)



def get_scenes(pages,threshold=0.025,max_chars=1400,min_chars = 400):
    sentences =extract_sentences(pages)
    texts = [s["text"] for s in sentences]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit(texts)

    scenes, buffer = [], []
    buffer_len,scene_id = 0,1
    lowsim_st = 0
    for _,sent in enumerate(sentences):
       
        if not buffer:
            scene_st_page = sent["page"]
            scene_st_char = sent["char_st"]
        if buffer and buffer_len>min_chars:
            sim = get_similarity(buffer,sent,vectorizer)
            print(f"sim scene {scene_id} and next sent sim = {sim:.3f}")
            
            if sim< threshold:
                lowsim_st+=1
            else:
                lowsim_st=0
            if lowsim_st>=5:
                text = " ".join(s["text"] for s in buffer)
                scene_en_page = buffer[-1]["page"]
                scene_en_char = buffer[-1]["char_en"]

                scenes.append(Scene(
                    scene_id= scene_id,
                    text = text,
                    start_page=scene_st_page,
                    end_page=scene_en_page,
                    char_start=scene_st_char,
                    char_end=scene_en_char
                ))

                scene_id+=1
                buffer=[]
                buffer_len = 0
                lowsim_st = 0

                scene_st_page = sent["page"]
                scene_st_char = sent["char_st"]

        buffer.append(sent)
        buffer_len += len(sent["text"])

        if buffer_len >= max_chars:
            text = " ".join(s["text"] for s in buffer)
            scene_en_page = buffer[-1]["page"]
            scene_en_char = buffer[-1]["char_en"]

            scenes.append(Scene(
                scene_id=scene_id,
                text=text,
                start_page=scene_st_page,
                end_page=scene_en_page,
                char_start=scene_st_char,
                char_end=scene_en_char
            ))
            scene_id += 1
            buffer = []
            buffer_len = 0
            lowsim_st = 0
    
    if buffer:
        text = " ".join(s["text"] for s in buffer)
        scene_en_page = buffer[-1]["page"]
        scene_en_char = buffer[-1]["char_en"]

        scenes.append(Scene(
                scene_id=scene_id,
                text=text,
                start_page=scene_st_page,
                end_page=scene_en_page,
                char_start=scene_st_char,
                char_end=scene_en_char
            ))
    final = []
    for sc in scenes:
        if final and len(sc.text) < 250:
            final[-1].text += " " + sc.text
            final[-1].end_page = sc.end_page
            final[-1].char_end = sc.char_end
        else:
            final.append(sc)

    return scenes