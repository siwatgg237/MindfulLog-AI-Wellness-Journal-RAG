"""
============================================================
  MindfulLog — Streamlit Frontend (ui/app.py)
============================================================
  A clean, calming interface for journaling and receiving
  AI-powered wellness insights.
============================================================
"""

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🧠 MindfulLog — AI Wellness Journal",
    page_icon="🧘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS — calming, modern aesthetic
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* ---------- Global ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Header ---------- */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6C63FF 0%, #48C6EF 50%, #6F86D6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .main-header p {
        color: #8892b0;
        font-size: 1.05rem;
        font-weight: 300;
    }

    /* ---------- Cards ---------- */
    .insight-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    }
    .insight-card h3 {
        color: #48C6EF;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .insight-card p, .insight-card li {
        color: #ccd6f6;
        line-height: 1.7;
    }

    /* ---------- Sentiment Badge ---------- */
    .sentiment-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.3rem 0.3rem 0.3rem 0;
    }
    .badge-emotion {
        background: rgba(108, 99, 255, 0.2);
        color: #6C63FF;
        border: 1px solid rgba(108, 99, 255, 0.3);
    }
    .badge-intensity-low {
        background: rgba(72, 198, 239, 0.15);
        color: #48C6EF;
        border: 1px solid rgba(72, 198, 239, 0.3);
    }
    .badge-intensity-moderate {
        background: rgba(255, 193, 7, 0.15);
        color: #FFC107;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    .badge-intensity-high {
        background: rgba(255, 82, 82, 0.15);
        color: #FF5252;
        border: 1px solid rgba(255, 82, 82, 0.3);
    }

    /* ---------- Exercise Card ---------- */
    .exercise-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 100%);
        border: 1px solid rgba(72, 198, 239, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.8rem 0;
    }
    .exercise-card h3 {
        color: #48C6EF;
    }
    .exercise-meta {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
        margin-top: 0.5rem;
    }
    .exercise-meta span {
        background: rgba(72, 198, 239, 0.1);
        color: #48C6EF;
        padding: 0.2rem 0.7rem;
        border-radius: 12px;
        font-size: 0.8rem;
        border: 1px solid rgba(72, 198, 239, 0.15);
    }

    /* ---------- Divider ---------- */
    .section-divider {
        border: none;
        border-top: 1px solid rgba(108, 99, 255, 0.15);
        margin: 1.5rem 0;
    }

    /* ---------- Footer ---------- */
    .footer {
        text-align: center;
        color: #5a6785;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
    }
    .footer a { color: #6C63FF; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# API Configuration
# ---------------------------------------------------------------------------
API_URL = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🧠 MindfulLog</h1>
    <p>Your AI-powered wellness companion — write freely, heal gently.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Journal Input
# ---------------------------------------------------------------------------
st.markdown("#### 📝 How are you feeling today?")
st.caption("Write openly about your thoughts, feelings, or anything on your mind. "
           "Your words stay private — the AI is here to listen and help.")

journal_text = st.text_area(
    label="Journal Entry",
    placeholder=(
        "Today was tough. I had a disagreement with a close friend and I can't "
        "stop thinking about it. I feel a knot in my stomach and my mind keeps "
        "racing with what I should have said differently..."
    ),
    height=180,
    label_visibility="collapsed",
)

# Submit button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit = st.button(
        "🔮 Get Wellness Insights",
        use_container_width=True,
        type="primary",
    )

# ---------------------------------------------------------------------------
# Process & Display Results
# ---------------------------------------------------------------------------
if submit:
    if not journal_text or len(journal_text.strip()) < 10:
        st.warning("✏️ Please write at least a few sentences so the AI can help you.")
    else:
        with st.spinner("🧘 Analyzing your journal entry and finding the best guidance..."):
            try:
                response = requests.post(
                    f"{API_URL}/journal",
                    json={"text": journal_text},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()

                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

                # --- Sentiment Analysis ---
                sentiment = data["sentiment"]
                intensity = sentiment["intensity"]
                intensity_class = f"badge-intensity-{intensity}"

                st.markdown(f"""
                <div class="insight-card">
                    <h3>💭 Emotional Analysis</h3>
                    <p>{sentiment["summary"]}</p>
                    <div style="margin-top: 0.8rem;">
                        <span class="sentiment-badge badge-emotion">
                            {sentiment["primary_emotion"].title()}
                        </span>
                        <span class="sentiment-badge {intensity_class}">
                            Intensity: {intensity.title()}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- Recommended Exercise ---
                exercise = data["recommended_exercise"]
                st.markdown(f"""
                <div class="exercise-card">
                    <h3>🧘 Recommended Exercise</h3>
                    <p style="color: #e6f1ff; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.3rem;">
                        {exercise["title"]}
                    </p>
                    <div class="exercise-meta">
                        <span>📂 {exercise["category"]}</span>
                        <span>⏱ {exercise["duration_minutes"]} min</span>
                        <span>📊 {exercise["difficulty"].title()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- AI Response ---
                st.markdown(f"""
                <div class="insight-card">
                    <h3>🤖 MindfulLog's Response</h3>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(data["ai_response"])

            except requests.exceptions.ConnectionError:
                st.error(
                    "🔌 **Cannot connect to the MindfulLog API.**\n\n"
                    "Make sure the FastAPI server is running:\n"
                    "```bash\nuvicorn api.main:app --reload --port 8000\n```"
                )
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ API Error: {e.response.text}")
            except Exception as e:
                st.error(f"❌ Something went wrong: {str(e)}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p>
        🧠 <strong>MindfulLog</strong> — AI Wellness Journal with RAG<br>
        Built for the <a href="#">OpenAI Codex x AIAT Hackathon</a> &nbsp;•&nbsp;
        Privacy-First &nbsp;•&nbsp; Post-AGI Wellness
    </p>
</div>
""", unsafe_allow_html=True)
