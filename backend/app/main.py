from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.ocr import extract_text
from core.cleaner import clean_text
from core.segmenter import get_scenes
app = FastAPI(title="ImStory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "backend running"}

if __name__ == "__main__":
    texts = extract_text('./storage/nairi.pdf')
    print(texts)
    for i,text in enumerate(texts):
        texts[i]["text"] = clean_text(text["text"])
    print(texts)
    scenes = get_scenes(texts)
    for s in scenes:
        print("\n","-"*70)
        print("Scene:", s.scene_id)
        print(s.text)