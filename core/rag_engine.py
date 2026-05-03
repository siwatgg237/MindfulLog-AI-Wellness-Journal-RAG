"""
============================================================
  MindfulLog — RAG Engine (core/rag_engine.py)
============================================================
  Heart of the AI pipeline:
    1. Load & embed mindfulness exercises → ChromaDB
    2. Analyze sentiment of a user's journal entry (GPT-4 Turbo)
    3. Retrieve the most relevant exercise via similarity search
    4. Compose a warm, actionable wellness response
============================================================
"""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document, HumanMessage, SystemMessage

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4-turbo")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "mindfulness_exercises.json"
CHROMA_DIR = PROJECT_ROOT / CHROMA_PERSIST_DIR

# Collection name inside ChromaDB
COLLECTION_NAME = "mindfulness_exercises"


# ---------------------------------------------------------------------------
# 1. Data Loading — convert JSON exercises into LangChain Documents
# ---------------------------------------------------------------------------
def load_exercises() -> list[Document]:
    """
    Read mindfulness_exercises.json and convert each exercise
    into a LangChain Document with rich page_content for embedding
    and metadata for display.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        exercises: list[dict[str, Any]] = json.load(f)

    documents: list[Document] = []
    for ex in exercises:
        # Build a rich text block so the embeddings capture semantics
        steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(ex["instructions"]))
        emotions = ", ".join(ex["target_emotions"])

        page_content = (
            f"Title: {ex['title']}\n"
            f"Category: {ex['category']}\n"
            f"Target Emotions: {emotions}\n"
            f"Duration: {ex['duration_minutes']} minutes\n"
            f"Difficulty: {ex['difficulty']}\n\n"
            f"Description:\n{ex['description']}\n\n"
            f"Instructions:\n{steps}\n\n"
            f"Scientific Basis:\n{ex['scientific_basis']}"
        )

        documents.append(
            Document(
                page_content=page_content,
                metadata={
                    "id": ex["id"],
                    "title": ex["title"],
                    "category": ex["category"],
                    "target_emotions": emotions,
                    "duration_minutes": ex["duration_minutes"],
                    "difficulty": ex["difficulty"],
                },
            )
        )

    return documents


# ---------------------------------------------------------------------------
# 2. Vector Store — embed documents into ChromaDB
# ---------------------------------------------------------------------------
def get_vector_store(force_rebuild: bool = False) -> Chroma:
    """
    Create or load a ChromaDB vector store with OpenAI embeddings.
    If *force_rebuild* is True, the store is recreated from scratch.
    """
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )

    chroma_dir = str(CHROMA_DIR)

    # If the store already exists and we don't need to rebuild, just load it
    if Path(chroma_dir).exists() and not force_rebuild:
        return Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=chroma_dir,
            embedding_function=embeddings,
        )

    # Otherwise, build from our JSON data
    documents = load_exercises()
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=chroma_dir,
    )
    return vector_store


# ---------------------------------------------------------------------------
# 3. Sentiment Analysis — use GPT-4 Turbo to understand the journal entry
# ---------------------------------------------------------------------------
def analyze_sentiment(entry: str) -> dict[str, str]:
    """
    Analyze the emotional tone of a journal entry.
    Returns a dict with 'primary_emotion', 'intensity', and 'summary'.
    """
    llm = ChatOpenAI(
        model=CHAT_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0.3,
    )

    system_prompt = (
        "You are a compassionate mental-health AI assistant. "
        "Analyze the following journal entry and return ONLY a JSON object with:\n"
        '  "primary_emotion": the dominant emotion (e.g. anxiety, sadness, anger, stress, loneliness),\n'
        '  "intensity": one of "low", "moderate", "high",\n'
        '  "summary": a brief 1-2 sentence empathetic summary of how the person is feeling.\n'
        "Respond ONLY with valid JSON — no markdown, no extra text."
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=entry),
    ])

    # Parse the JSON response robustly
    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback if the model wraps in markdown code fences
        import re
        json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {
                "primary_emotion": "unknown",
                "intensity": "moderate",
                "summary": response.content,
            }

    return result


# ---------------------------------------------------------------------------
# 4. RAG Pipeline — retrieve relevant exercise & generate a response
# ---------------------------------------------------------------------------
def retrieve_relevant_exercise(query: str, k: int = 1) -> list[Document]:
    """Retrieve the top-k most relevant exercises from ChromaDB."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results


def generate_wellness_response(journal_entry: str) -> dict[str, Any]:
    """
    End-to-end RAG pipeline:
      1. Analyze sentiment of the journal entry
      2. Retrieve the most relevant mindfulness exercise
      3. Generate a warm, personalized response
    Returns a dict with sentiment, exercise info, and the AI response.
    """
    # Step 1 — Sentiment
    sentiment = analyze_sentiment(journal_entry)

    # Step 2 — Retrieval (combine entry + detected emotion for better search)
    search_query = f"{journal_entry}\nEmotion: {sentiment['primary_emotion']}"
    retrieved_docs = retrieve_relevant_exercise(search_query, k=2)

    # Build context from retrieved exercises
    exercise_context = "\n\n---\n\n".join(doc.page_content for doc in retrieved_docs)

    # Step 3 — Generation
    llm = ChatOpenAI(
        model=CHAT_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0.7,
    )

    system_prompt = (
        "You are MindfulLog, a warm and compassionate AI wellness companion. "
        "You have access to mindfulness exercises retrieved from a curated database. "
        "Your role is to:\n"
        "  1. Acknowledge the user's feelings with genuine empathy.\n"
        "  2. Provide a brief, insightful reflection on their journal entry.\n"
        "  3. Recommend the most suitable exercise from the retrieved context below.\n"
        "  4. Walk them through the exercise in a gentle, step-by-step manner.\n"
        "  5. End with an encouraging, hopeful message.\n\n"
        "Keep your response warm, human, and under 300 words.\n"
        "Use soft formatting (bullet points, short paragraphs) for readability.\n\n"
        f"--- Retrieved Mindfulness Exercises ---\n{exercise_context}\n"
        f"--- End of Exercises ---"
    )

    user_prompt = (
        f"Here is the user's journal entry:\n\n\"{journal_entry}\"\n\n"
        f"Detected emotion: {sentiment['primary_emotion']} "
        f"(intensity: {sentiment['intensity']})\n"
        f"Emotional summary: {sentiment['summary']}"
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    # Extract metadata from the top retrieved exercise
    top_exercise = retrieved_docs[0] if retrieved_docs else None
    exercise_info = {
        "title": top_exercise.metadata.get("title", "N/A") if top_exercise else "N/A",
        "category": top_exercise.metadata.get("category", "N/A") if top_exercise else "N/A",
        "duration_minutes": top_exercise.metadata.get("duration_minutes", 0) if top_exercise else 0,
        "difficulty": top_exercise.metadata.get("difficulty", "N/A") if top_exercise else "N/A",
    }

    return {
        "sentiment": sentiment,
        "recommended_exercise": exercise_info,
        "ai_response": response.content,
    }


# ---------------------------------------------------------------------------
# CLI Quick Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🧠 MindfulLog RAG Engine — Quick Test")
    print("=" * 50)

    # Rebuild vector store
    print("📦 Building vector store from mindfulness exercises...")
    vs = get_vector_store(force_rebuild=True)
    print(f"✅ Vector store ready ({vs._collection.count()} documents embedded)")

    # Test with a sample entry
    test_entry = (
        "I had a terrible day at work. My manager criticized my presentation "
        "in front of everyone and I felt so embarrassed. I can't stop replaying "
        "the moment in my head. I feel anxious and can't sleep."
    )
    print(f"\n📝 Test Entry:\n{test_entry}\n")
    print("🔄 Processing...\n")

    result = generate_wellness_response(test_entry)

    print(f"💭 Sentiment: {result['sentiment']}")
    print(f"🧘 Recommended: {result['recommended_exercise']['title']}")
    print(f"\n🤖 AI Response:\n{result['ai_response']}")
