import os
import shutil
import uuid
import threading
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .core.ocr import extract_text
from .core.cleaner import clean_text
from .services import nlp_service, comfy_service

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"
GEN_LOCK = threading.Lock()
app = FastAPI(title="ImStory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_STORAGE = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")
)
UPLOAD_DIR = os.path.join(BASE_STORAGE, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/generate")
async def generate_story(file: UploadFile = File(...)):
    start_time = time.time()

    file_uid = str(uuid.uuid4())
    filename = f"{file_uid}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    try:
        raw_pages = extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    if not raw_pages:
        raise HTTPException(status_code=400, detail="No text extracted from PDF")

    ocr_done = time.time()

    cleaned_texts = []
    for p in raw_pages:
        cleaned_texts.append(clean_text(p["text"]))

    try:
        prompt_results = nlp_service.generate_prompts(cleaned_texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP Generation failed: {str(e)}")

    nlp_done = time.time()

    try:
        with GEN_LOCK:
            image_results = comfy_service.generate_images(file_uid, prompt_results)
    except Exception as e:
        image_results = [{"error": str(e)}]

    end_time = time.time()

    return {
        "uid": file_uid,
        "story_data": prompt_results,
        "images": image_results,
        "timing": {
            "ocr_time": round(ocr_done - start_time, 2),
            "nlp_time": round(nlp_done - ocr_done, 2),
            "image_time": round(end_time - nlp_done, 2),
            "total_time": round(end_time - start_time, 2),
        },
    }


@app.get("/")
def root():
    return {"status": "backend running"}
