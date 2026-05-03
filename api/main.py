"""
============================================================
  MindfulLog — FastAPI Backend (api/main.py)
============================================================
  Endpoints:
    POST /journal     — Submit a journal entry, get AI response
    GET  /health      — Health check
    POST /rebuild-db  — Rebuild the ChromaDB vector store
============================================================
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.rag_engine import generate_wellness_response, get_vector_store


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class JournalEntry(BaseModel):
    """Request body for the /journal endpoint."""
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The user's journal entry text (10-5000 characters).",
        json_schema_extra={"example": "I've been feeling really anxious about my upcoming exam..."},
    )


class SentimentResult(BaseModel):
    primary_emotion: str
    intensity: str
    summary: str


class ExerciseResult(BaseModel):
    title: str
    category: str
    duration_minutes: int
    difficulty: str


class JournalResponse(BaseModel):
    """Response body returned from the /journal endpoint."""
    sentiment: SentimentResult
    recommended_exercise: ExerciseResult
    ai_response: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


# ---------------------------------------------------------------------------
# Application Lifespan — initialize vector store on startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the ChromaDB vector store when the server starts."""
    print("🚀 MindfulLog API starting up...")
    try:
        vs = get_vector_store(force_rebuild=False)
        doc_count = vs._collection.count()
        print(f"✅ Vector store loaded — {doc_count} documents ready")
    except Exception as e:
        print(f"⚠️  Vector store initialization skipped: {e}")
    yield
    print("👋 MindfulLog API shutting down.")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="🧠 MindfulLog API",
    description=(
        "A privacy-first AI journal that uses RAG to provide "
        "personalized mental wellness insights based on your past entries "
        "and a curated database of mindfulness techniques."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow CORS for the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Simple health-check endpoint."""
    return HealthResponse(
        status="healthy",
        service="MindfulLog API",
        version="1.0.0",
    )


@app.post("/journal", response_model=JournalResponse, tags=["Journal"])
async def process_journal_entry(entry: JournalEntry):
    """
    Submit a journal entry and receive:
      - Sentiment analysis (emotion, intensity, summary)
      - A recommended mindfulness exercise
      - A personalized, comforting AI response
    """
    try:
        result = generate_wellness_response(entry.text)
        return JournalResponse(
            sentiment=SentimentResult(**result["sentiment"]),
            recommended_exercise=ExerciseResult(**result["recommended_exercise"]),
            ai_response=result["ai_response"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process journal entry: {str(e)}",
        )


@app.post("/rebuild-db", tags=["System"])
async def rebuild_vector_store():
    """Force-rebuild the ChromaDB vector store from the JSON data."""
    try:
        vs = get_vector_store(force_rebuild=True)
        count = vs._collection.count()
        return {"status": "success", "documents_embedded": count}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rebuild vector store: {str(e)}",
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
