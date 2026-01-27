from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.ocr import extract_text
from core.cleaner import clean_text
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
    pages = extract_text("./storage/nairi.pdf")

    for p in pages:
        p.text = clean_text(p.text)
        print("\n" + "-" * 80)
        print(f"PAGE {p.pn}\n")
        print(p.text[:800], "...\n")
