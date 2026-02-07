from fastapi import FastAPI
from pydantic import BaseModel
from pipeline import StoryPipeline
import uvicorn

app = FastAPI(title="NLP Service")

print("Loading NLP Pipeline...")
pipeline = StoryPipeline()
print("NLP Pipeline Loaded.")


class TextRequest(BaseModel):
    pages: list[str]


@app.post("/process")
def process(req: TextRequest):
    return pipeline.process(req.pages)


@app.get("/")
def root():
    return {"status": "nlp running"}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=9000)
