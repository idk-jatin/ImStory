# ImStory

ImStory is a project I built to turn written stories into visual scenes using AI. The system reads a PDF, tries to understand what’s happening in the story, and then generates images for each scene using Stable Diffusion through ComfyUI.

The main goal wasn’t just image generation, it was seeing whether an AI pipeline could maintain story context, like remembering characters, mood shifts, locations, and visual continuity across scenes.

---

## What It Does

### Text Understanding (NLP Layer)
I used spaCy transformer models plus custom logic to extract:
-   **characters and entities**
-   **actions and relationships**
-   **emotional tone**
-   **environmental cues**


### Character Continuity
One of the biggest problems i faced with AI image generation is consistency. I built a memory system that:
-   tracks characters across pages
-   stores clothing or visual attributes
-   keeps scene context alive

### Scene Direction Logic
The system automatically derives cinematic details like:
-   **camera framing** 
-   **lighting style** 
-   **atmospheric descriptors**

### Image Generation Pipeline
-   **ComfyUI workflow automation**
-   **JSON prompt injection**
-   **seed consistency handling**

### Frontend Interface
There’s also a React frontend that allows:
-   uploading story documents
-   running generation
-   viewing results page by page

---

## Architecture Overview
The project has three main layers:

### Backend (FastAPI)
Handles:
-   uploads
-   OCR/text cleaning
-   NLP orchestration
-   image generation coordination

### NLP Engine
Core logic layer with:
-   spaCy transformer pipeline
-   FastCoref for coreference resolution
-   custom entity typing and world memory
-   mood/atmosphere extraction
-   prompt building logic

### Image Generation Layer
ComfyUI Stable Diffusion setup:
-   workflow based generation
-   seed stabilization
-   negative prompt control

---

## Technical Things I Focused On

-   **maintaining cross-scene character consistency**
-   **automatic cinematic prompt engineering**
-   **balancing NLP structure**

---

## Why I Built This

Mostly for exploring NLP:
-   Can story understanding actually guide image generation?
-   How far can prompt engineering + NLP memory go?
-   What would a multimodal storytelling pipeline look like?

It also helped me learn a lot about:
-   NLP pipelines
-   generative diffusion workflows
-   system integration challenges

---

Things I’d like to add in future:
-   RAG based story grounding
-   better character visual embeddings
-   LoRA based style consistency
