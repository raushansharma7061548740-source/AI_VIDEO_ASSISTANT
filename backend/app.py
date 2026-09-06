"""
FastAPI backend for the AI Video Assistant.

Exposes:
  POST /api/process        - process a YouTube URL OR an uploaded file
  POST /api/chat           - ask a question about an already-processed video
  GET  /api/session/{id}   - fetch results for a session (title/summary/etc.)
  GET  /                   - serves the frontend (static/index.html)

Run with:
  uv run uvicorn app:app --reload
"""

import os
import shutil
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utlis.audio_processing import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

app = FastAPI(title="AI Video Assistant API")

# Allow the frontend (served from anywhere during dev) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory store: session_id -> { transcript, title, summary, ..., rag_chain }
# NOTE: this resets when the server restarts. Fine for local/dev use.
# For production, swap this for a real DB + persisted vector store lookup.
SESSIONS: dict[str, dict] = {}


class ChatRequest(BaseModel):
    session_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str


class ProcessResponse(BaseModel):
    session_id: str
    title: str
    summary: str
    action_items: str
    key_decisions: str
    open_questions: str


def _run_pipeline(source: str) -> dict:
    """Runs the full pipeline on a source (YouTube URL or local file path)."""
    chunks = process_input(source)
    transcript = transcribe_all(chunks)

    title = generate_title(transcript)
    summary = summarize(transcript)
    action_items = extract_action_items(transcript)
    key_decisions = extract_key_decisions(transcript)
    open_questions = extract_questions(transcript)
    rag_chain = build_rag_chain(transcript)

    return {
        "transcript": transcript,
        "title": title,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": open_questions,
        "rag_chain": rag_chain,
    }


@app.post("/api/process", response_model=ProcessResponse)
async def process_video(
    youtube_url: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
):
    """
    Accepts EITHER a youtube_url form field OR an uploaded file (not both).
    Runs the full pipeline and returns a session_id plus the results.
    """
    if not youtube_url and not file:
        raise HTTPException(
            status_code=400,
            detail="Provide either a youtube_url or a file upload.",
        )

    if youtube_url and file:
        raise HTTPException(
            status_code=400,
            detail="Provide only one of youtube_url or file, not both.",
        )

    # Case 1: YouTube URL — pass straight through, download happens inside the pipeline
    if youtube_url:
        source = youtube_url
    # Case 2: uploaded file — save it to disk first, pipeline needs a path
    else:
        ext = os.path.splitext(file.filename)[1] or ".mp4"
        saved_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
        with open(saved_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        source = saved_path

    try:
        result = _run_pipeline(source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = result

    return ProcessResponse(
        session_id=session_id,
        title=result["title"],
        summary=result["summary"],
        action_items=result["action_items"],
        key_decisions=result["key_decisions"],
        open_questions=result["open_questions"],
    )


@app.get("/api/session/{session_id}", response_model=ProcessResponse)
async def get_session(session_id: str):
    """Re-fetch results for a session (e.g. after a page refresh)."""
    result = SESSIONS.get(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found.")

    return ProcessResponse(
        session_id=session_id,
        title=result["title"],
        summary=result["summary"],
        action_items=result["action_items"],
        key_decisions=result["key_decisions"],
        open_questions=result["open_questions"],
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Ask a question about a previously-processed video's transcript."""
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    rag_chain = session["rag_chain"]
    answer = ask_question(rag_chain, req.question)
    return ChatResponse(answer=answer)


# Serve the frontend. app.py lives in backend/, and frontend/ is a sibling
# folder one level up (project_root/frontend), so resolve it relative to
# this file's actual location on disk.
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")