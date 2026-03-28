import streamlit as st
import json
import os
import base64
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Config & Constants
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Black Girl STEM Summit - Viral Trend Vote",
    page_icon="🎓",
    layout="wide",
)

VOTES_FILE = Path(__file__).parent / "votes.json"

TRENDS = [
    {
        "name": "Amapiano",
        "emoji": "🎶",
        "image": "Ampiano_09_04_32.png",
        "description": "The South-African born Amapiano dance trend took over every timeline!",
    },
    {
        "name": "Marching Band",
        "emoji": "🥁",
        "image": "Marching Band_09_04_24.png",
        "description": "HBCU marching bands showed out and the internet couldn't stop watching!",
    },
    {
        "name": "Step Team",
        "emoji": "👢",
        "image": "Step Team_09_04_28.png",
        "description": "Precision stepping went viral — stomp, clap, repeat!",
    },
    {
        "name": "Trombone Solo",
        "emoji": "🎺",
        "image": "Trombone Solo_09_04_16.png",
        "description": "One trombone, millions of views. Brass never sounded so cool!",
    },
    {
        "name": "Wash Day",
        "emoji": "💆🏾‍♀️",
        "image": "Wash Day_09_04_19.png",
        "description": "Wash-day routines became the most relatable trend on social media!",
    },
]

# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def load_votes() -> dict[str, int]:
    if VOTES_FILE.exists():
        with open(VOTES_FILE, "r") as f:
            return json.load(f)
    return {t["name"]: 0 for t in TRENDS}


def save_votes(votes: dict[str, int]):
    with open(VOTES_FILE, "w") as f:
        json.dump(votes, f)


def img_to_base64(path: str) -> str:
    full = Path(__file__).parent / path
    with open(full, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------------------
# Custom CSS — Meharry Medical College palette
# Navy #00205B  |  Gold #C8A951  |  White #FFFFFF
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&display=swap');

    /* ---------- global ---------- */
    html, body, [class*="stApp"] {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #00205B 0%, #001440 60%, #0a0a2e 100%);
    }

    /* ---------- hero ---------- */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1rem;
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #C8A951 0%, #ffe08a 50%, #C8A951 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }
    .hero .subtitle {
        color: #ffffffcc;
        font-size: 1.15rem;
        margin-top: 0.25rem;
    }
    .hero .hosted {
        color: #C8A951;
        font-weight: 600;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    .divider {
        width: 120px;
        height: 3px;
        background: linear-gradient(90deg, transparent, #C8A951, transparent);
        margin: 1rem auto 2rem;
        border-radius: 2px;
    }

    /* ---------- trend cards ---------- */
    .trend-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(200,169,81,0.25);
        border-radius: 20px;
        padding: 1.8rem 1.2rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        backdrop-filter: blur(6px);
    }
    .trend-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(200,169,81,0.18);
    }
    .trend-card .trend-emoji {
        font-size: 2.5rem;
    }
    .trend-card .trend-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #C8A951;
        margin: 0.4rem 0 0.2rem;
    }
    .trend-card .trend-desc {
        color: #ffffffbb;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    .trend-card img.qr {
        width: 160px;
        height: 160px;
        margin: 1rem auto 0;
        border-radius: 12px;
        border: 2px solid #C8A951;
        background: #fff;
        padding: 6px;
    }

    /* ---------- vote button ---------- */
    .stButton > button {
        background: linear-gradient(135deg, #C8A951, #ffe08a) !important;
        color: #00205B !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: transform 0.15s, box-shadow 0.15s !important;
        letter-spacing: 0.3px !important;
        margin-top: 0.8rem !important;
    }
    .stButton > button:hover {
        transform: scale(1.04) !important;
        box-shadow: 0 4px 20px rgba(200,169,81,0.45) !important;
    }

    /* ---------- results bar ---------- */
    .result-bar-wrapper {
        margin: 0.5rem 0;
    }
    .result-label {
        color: #ffffffdd;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.2rem;
    }
    .result-bar-bg {
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        overflow: hidden;
        height: 36px;
        position: relative;
    }
    .result-bar-fill {
        height: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #C8A951, #ffe08a);
        display: flex;
        align-items: center;
        padding-left: 14px;
        font-weight: 700;
        font-size: 0.9rem;
        color: #00205B;
        transition: width 0.6s ease;
        min-width: 40px;
    }

    /* ---------- success toast ---------- */
    .vote-toast {
        background: linear-gradient(135deg, #C8A951, #ffe08a);
        color: #00205B;
        padding: 1rem 1.5rem;
        border-radius: 14px;
        text-align: center;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 1rem auto;
        max-width: 500px;
        animation: popIn 0.35s ease;
    }
    @keyframes popIn {
        0%   { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1);   opacity: 1; }
    }

    /* ---------- footer ---------- */
    .footer {
        text-align: center;
        color: #ffffff55;
        font-size: 0.8rem;
        padding: 3rem 0 1.5rem;
    }
    .footer a { color: #C8A951; text-decoration: none; }

    /* hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>BLACK GIRL STEM SUMMIT</h1>
        <div class="subtitle">Which viral trend hit the hardest? Cast your vote!</div>
        <div class="hosted">Hosted at Meharry Medical College &nbsp;|&nbsp; Nashville, TN</div>
    </div>
    <div class="divider"></div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "voted" not in st.session_state:
    st.session_state.voted = False
if "voted_for" not in st.session_state:
    st.session_state.voted_for = None

# ---------------------------------------------------------------------------
# Trend voting cards  (one row of 5 columns, or wrapping on mobile)
# ---------------------------------------------------------------------------

votes = load_votes()

cols = st.columns(len(TRENDS), gap="large")

for col, trend in zip(cols, TRENDS):
    with col:
        b64 = img_to_base64(trend["image"])
        st.markdown(
            f"""
            <div class="trend-card">
                <div class="trend-emoji">{trend["emoji"]}</div>
                <div class="trend-name">{trend["name"]}</div>
                <div class="trend-desc">{trend["description"]}</div>
                <img class="qr" src="data:image/png;base64,{b64}" alt="{trend['name']} QR code" />
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            f"Vote {trend['emoji']}  {trend['name']}",
            key=f"vote_{trend['name']}",
            disabled=st.session_state.voted,
        ):
            votes[trend["name"]] = votes.get(trend["name"], 0) + 1
            save_votes(votes)
            st.session_state.voted = True
            st.session_state.voted_for = trend["name"]
            st.rerun()

# ---------------------------------------------------------------------------
# Vote confirmation
# ---------------------------------------------------------------------------

if st.session_state.voted:
    st.markdown(
        f'<div class="vote-toast">You voted for {st.session_state.voted_for}! Thanks for making your voice heard! 🎉</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Live Results
# ---------------------------------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<h2 style="text-align:center;color:#C8A951;font-weight:800;margin-bottom:0.5rem;">Live Results</h2>',
    unsafe_allow_html=True,
)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

total = max(sum(votes.values()), 1)  # avoid div-by-zero

# Sort by votes descending
ranked = sorted(TRENDS, key=lambda t: votes.get(t["name"], 0), reverse=True)

for i, trend in enumerate(ranked):
    count = votes.get(trend["name"], 0)
    pct = count / total * 100
    rank_label = "👑 " if i == 0 and count > 0 else ""
    st.markdown(
        f"""
        <div class="result-bar-wrapper">
            <div class="result-label">{rank_label}{trend["emoji"]} {trend["name"]}</div>
            <div class="result-bar-bg">
                <div class="result-bar-fill" style="width:{max(pct, 4):.1f}%;">
                    {count} vote{"s" if count != 1 else ""} &nbsp;·&nbsp; {pct:.0f}%
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="footer">
        Black Girl STEM Summit {datetime.now().year} &nbsp;·&nbsp;
        <a href="#">Meharry Medical College</a> &nbsp;·&nbsp;
        Scan the QR codes to watch each trend!
    </div>
    """,
    unsafe_allow_html=True,
)
