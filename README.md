# 🧠 MindfulLog-AI-Wellness-Journal-RAG

> **A privacy-first AI journal that uses RAG (Retrieval-Augmented Generation) to provide personalized mental wellness insights.**

Built for the **OpenAI Codex x AIAT Hackathon** — Theme: *Wellness AI in the Post-AGI Era*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-FF6F00?style=for-the-badge)](https://trychroma.com)

---

## 🌅 The Post-AGI Vision

As AI systems grow increasingly powerful, the question isn't just *"What can AI do?"* — it's *"How can AI help humans stay human?"*

In a Post-AGI world, mental wellbeing becomes the most critical frontier. MindfulLog envisions a future where:

- 🧘 **AI is a wellness companion, not a replacement for human connection.** It gently guides users toward evidence-based mindfulness practices without diagnosing or prescribing.
- 🔒 **Privacy is non-negotiable.** Journal entries are processed locally and never stored beyond the session. Your thoughts belong to you alone.
- 🧬 **Personalization through RAG, not surveillance.** Instead of building a profile by tracking behavior, MindfulLog uses Retrieval-Augmented Generation to match your current emotional state with the right therapeutic technique — in real time.
- 🌱 **Human agency is preserved.** The AI suggests, but the human decides. This is therapy-informed, not therapy-replacing.

> *"In the age of superintelligence, the most revolutionary act is to be still, to breathe, and to feel."*

---

## 🏗️ Architecture

```
MindfulLog-AI-Wellness-Journal-RAG/
│
├── api/                      # 🔧 FastAPI Backend
│   ├── __init__.py
│   └── main.py               # REST API endpoints (/journal, /health)
│
├── core/                     # 🧠 AI Core (RAG Pipeline)
│   ├── __init__.py
│   └── rag_engine.py         # Sentiment analysis + ChromaDB retrieval + GPT-4 generation
│
├── data/                     # 📚 Knowledge Base
│   └── mindfulness_exercises.json  # Curated mindfulness techniques
│
├── ui/                       # 🎨 Streamlit Frontend
│   └── app.py                # User-facing journal interface
│
├── .env.example              # 🔑 Environment variable template
├── .gitignore                # 🚫 Git ignore rules
├── requirements.txt          # 📦 Python dependencies
└── README.md                 # 📖 This file
```

### Data Flow

```
User writes journal entry
        │
        ▼
   [Streamlit UI]  ──HTTP POST──▶  [FastAPI /journal]
                                        │
                                        ▼
                               [RAG Engine Pipeline]
                              ┌─────────┴──────────┐
                              ▼                     ▼
                    [GPT-4 Turbo]           [ChromaDB Search]
                    Sentiment Analysis      Retrieve top exercise
                              │                     │
                              └─────────┬───────────┘
                                        ▼
                               [GPT-4 Turbo]
                          Generate personalized response
                                        │
                                        ▼
                              Return to user:
                           • Sentiment analysis
                           • Recommended exercise
                           • Comforting AI response
```

---

## ⚡ Quick Start — Local Setup

### Prerequisites

- **Python 3.10+**
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MindfulLog-AI-Wellness-Journal-RAG.git
cd MindfulLog-AI-Wellness-Journal-RAG
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Start the FastAPI Backend

```bash
uvicorn api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive Swagger documentation.

### 6. Start the Streamlit Frontend (New Terminal)

```bash
streamlit run ui/app.py
```

The UI will open automatically at `http://localhost:8501`.

---

## 🧪 API Reference

### `POST /journal`

Submit a journal entry and receive a personalized wellness response.

**Request Body:**
```json
{
  "text": "I've been feeling really anxious about my upcoming presentation..."
}
```

**Response:**
```json
{
  "sentiment": {
    "primary_emotion": "anxiety",
    "intensity": "high",
    "summary": "The user is experiencing significant anxiety related to performance pressure."
  },
  "recommended_exercise": {
    "title": "Box Breathing (4-4-4-4)",
    "category": "Breathing",
    "duration_minutes": 5,
    "difficulty": "beginner"
  },
  "ai_response": "I hear you, and I want you to know that what you're feeling is completely valid..."
}
```

### `GET /health`

Health check endpoint.

### `POST /rebuild-db`

Force rebuild the ChromaDB vector store from the JSON knowledge base.

---

## 🧘 Mindfulness Knowledge Base

The `data/mindfulness_exercises.json` contains curated, evidence-based techniques:

| Exercise | Category | Target Emotions | Duration |
|----------|----------|----------------|----------|
| Box Breathing (4-4-4-4) | Breathing | Anxiety, Stress, Overwhelm | 5 min |
| Body Scan Meditation | Meditation | Tension, Insomnia, Restlessness | 15 min |
| Gratitude Journaling | Cognitive Reframing | Sadness, Negativity, Low Mood | 10 min |
| 5-4-3-2-1 Grounding | Grounding | Panic, Dissociation, Flashbacks | 5 min |
| Loving-Kindness (Metta) | Meditation | Self-criticism, Anger, Loneliness | 10 min |

---

## 🔒 Privacy & Ethics

- **No data persistence by default.** Journal entries are processed in-memory and discarded.
- **No user tracking.** We don't build behavioral profiles.
- **Not a replacement for professional help.** MindfulLog is a wellness companion, not a therapist. If you're in crisis, please reach out to a mental health professional.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Interactive journal UI |
| Backend | FastAPI + Uvicorn | REST API server |
| AI Engine | LangChain + GPT-4 Turbo | Sentiment analysis & response generation |
| Embeddings | text-embedding-3-small | Semantic search over exercises |
| Vector DB | ChromaDB | Local vector store for RAG |
| Config | python-dotenv | Environment management |

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

<p align="center">
  <strong>🧠 MindfulLog</strong> — Because in the age of AI, your peace of mind still matters most.<br>
  <em>Built with ❤️ for the OpenAI Codex x AIAT Hackathon</em>
</p>
