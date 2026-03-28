import streamlit as st
import json
import base64
import plotly.graph_objects as go
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

# ---- Trend data -----------------------------------------------------------
# actual_views: real-world view counts (update these with the real numbers!)
# actual_rank: 1 = most viral
TRENDS = [
    {
        "name": "Amapiano",
        "emoji": "🎶",
        "image": "Ampiano_09_04_32.png",
        "description": "The South-African born Amapiano dance trend took over every timeline!",
        "url": "https://www.tiktok.com/@itsracks_/video/7607621336860495122?lang=en&q=ampiano&t=1774705655240",
        "actual_views": 2_800_000_000,
        "actual_rank": 1,
    },
    {
        "name": "Marching Band",
        "emoji": "🥁",
        "image": "Marching Band_09_04_24.png",
        "description": "HBCU marching bands showed out and the internet couldn't stop watching!",
        "url": "https://www.youtube.com/watch?v=LOZPhxatVG4",
        "actual_views": 890_000_000,
        "actual_rank": 3,
    },
    {
        "name": "Step Team",
        "emoji": "👢",
        "image": "Step Team_09_04_28.png",
        "description": "Precision stepping went viral — stomp, clap, repeat!",
        "url": "https://www.tiktok.com/@dssdsorority/video/7610966238109486350?q=Step%20Team&t=1774706027938",
        "actual_views": 650_000_000,
        "actual_rank": 4,
    },
    {
        "name": "Trombone Solo",
        "emoji": "🎺",
        "image": "Trombone Solo_09_04_16.png",
        "description": "One trombone, millions of views. Brass never sounded so cool!",
        "url": "https://www.tiktok.com/@zachunter5454/video/7114289315127250222?q=Trumbone%20solo%20hbcu&t=1774706573425",
        "actual_views": 420_000_000,
        "actual_rank": 5,
    },
    {
        "name": "Wash Day",
        "emoji": "💆🏾‍♀️",
        "image": "Wash Day_09_04_19.png",
        "description": "Wash-day routines became the most relatable trend on social media!",
        "url": "https://www.youtube.com/watch?v=fPHN__p5Pw0",
        "actual_views": 1_200_000_000,
        "actual_rank": 2,
    },
]

TREND_LOOKUP = {t["name"]: t for t in TRENDS}

# Meharry Medical College official palette
MAROON = "#6A173B"
MAROON_DARK = "#3B1526"
MAROON_DEEP = "#270E19"
GOLD = "#FFE293"
GOLD_LIGHT = "#FFF0C2"
WHITE = "#FFFFFF"

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


def format_views(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.0f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


# ---------------------------------------------------------------------------
# Custom CSS — Meharry Medical College palette
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700;900&family=Nunito:wght@400;700&display=swap');

    html, body, [class*="stApp"] { font-family: 'Nunito Sans', sans-serif; }
    .stApp {
        background: linear-gradient(135deg, #6A173B 0%, #3B1526 60%, #270E19 100%);
    }

    /* hero */
    .hero { text-align: center; padding: 2.5rem 1rem 1rem; }
    .hero h1 {
        font-size: 3rem; font-weight: 900;
        background: linear-gradient(90deg, #FFE293, #FFF0C2, #FFE293);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0; letter-spacing: -0.5px;
    }
    .hero .subtitle { color: #ffffffcc; font-size: 1.15rem; margin-top: 0.25rem; }
    .hero .hosted  { color: #FFE293; font-weight: 600; font-size: 0.95rem; margin-top: 0.3rem; }
    .hero .hashtags {
        color: #FFF0C2; font-weight: 800; font-size: 1.3rem;
        margin-top: 0.6rem; letter-spacing: 1px;
        text-shadow: 0 0 20px rgba(255,226,147,0.3);
    }
    .divider {
        width: 120px; height: 3px;
        background: linear-gradient(90deg, transparent, #FFE293, transparent);
        margin: 1rem auto 2rem; border-radius: 2px;
    }

    /* trend cards */
    .trend-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,226,147,0.25);
        border-radius: 20px; padding: 1.8rem 1.2rem;
        text-align: center; transition: transform 0.2s, box-shadow 0.2s;
        backdrop-filter: blur(6px);
    }
    .trend-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(255,226,147,0.18);
    }
    .trend-card .trend-emoji { font-size: 2.5rem; }
    .trend-card .trend-name  { font-size: 1.4rem; font-weight: 700; color: #FFE293; margin: 0.4rem 0 0.2rem; }
    .trend-card .trend-desc  { color: #ffffffbb; font-size: 0.92rem; line-height: 1.45; }
    .trend-card img.qr {
        width: 160px; height: 160px; margin: 1rem auto 0;
        border-radius: 12px; border: 2px solid #FFE293;
        background: #fff; padding: 6px;
    }
    .trend-card .watch-link {
        display: inline-block; margin-top: 0.7rem;
        color: #FFF0C2; font-weight: 700; font-size: 0.95rem;
        text-decoration: none; padding: 0.35rem 1rem;
        border: 2px solid #FFE293; border-radius: 50px;
        transition: background 0.2s, color 0.2s;
    }
    .trend-card .watch-link:hover {
        background: #FFE293; color: #6A173B;
    }

    /* buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FFE293, #FFF0C2) !important;
        color: #6A173B !important; font-weight: 700 !important;
        font-size: 1.05rem !important; border: none !important;
        border-radius: 50px !important; padding: 0.6rem 2rem !important;
        width: 100% !important; cursor: pointer !important;
        transition: transform 0.15s, box-shadow 0.15s !important;
        letter-spacing: 0.3px !important; margin-top: 0.8rem !important;
    }
    .stButton > button:hover {
        transform: scale(1.04) !important;
        box-shadow: 0 4px 20px rgba(255,226,147,0.45) !important;
    }

    /* result bars */
    .result-bar-wrapper { margin: 0.5rem 0; }
    .result-label { color: #ffffffdd; font-weight: 600; font-size: 1rem; margin-bottom: 0.2rem; }
    .result-bar-bg {
        background: rgba(255,255,255,0.1); border-radius: 12px;
        overflow: hidden; height: 36px; position: relative;
    }
    .result-bar-fill {
        height: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #FFE293, #FFF0C2);
        display: flex; align-items: center; padding-left: 14px;
        font-weight: 700; font-size: 0.9rem; color: #6A173B;
        transition: width 0.6s ease; min-width: 40px;
    }

    /* toast */
    .vote-toast {
        background: linear-gradient(135deg, #FFE293, #FFF0C2);
        color: #6A173B; padding: 1rem 1.5rem; border-radius: 14px;
        text-align: center; font-weight: 700; font-size: 1.1rem;
        margin: 1rem auto; max-width: 500px;
        animation: popIn 0.35s ease;
    }
    @keyframes popIn { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

    /* section headers */
    .section-head {
        text-align: center; color: #FFE293; font-weight: 800;
        font-size: 1.8rem; margin-bottom: 0.3rem;
    }

    /* match badges */
    .match-perfect { color: #4ade80; font-weight: 700; }
    .match-close   { color: #fbbf24; font-weight: 700; }
    .match-off     { color: #f87171; font-weight: 700; }

    /* score card */
    .score-card {
        background: rgba(255,255,255,0.08); border: 2px solid #FFE293;
        border-radius: 20px; padding: 2rem; text-align: center;
        max-width: 480px; margin: 1.5rem auto;
    }
    .score-card .big-number {
        font-size: 4rem; font-weight: 900; color: #FFE293; line-height: 1;
    }
    .score-card .score-label {
        color: #ffffffcc; font-size: 1.1rem; margin-top: 0.3rem;
    }

    /* footer */
    .footer { text-align: center; color: #ffffff55; font-size: 0.8rem; padding: 3rem 0 1.5rem; }
    .footer a { color: #FFE293; text-decoration: none; }

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
        <div class="hashtags">#BGISS2026 &nbsp;&nbsp; #MMCSTEAMSUMMIT</div>
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
if "revealed" not in st.session_state:
    st.session_state.revealed = False

# ---------------------------------------------------------------------------
# Trend voting cards
# ---------------------------------------------------------------------------

votes = load_votes()
cols = st.columns(len(TRENDS), gap="large")

for col, trend in zip(cols, TRENDS):
    with col:
        b64 = img_to_base64(trend["image"])
        platform = "TikTok" if "tiktok.com" in trend["url"] else "YouTube"
        st.markdown(
            f"""
            <div class="trend-card">
                <div class="trend-emoji">{trend["emoji"]}</div>
                <div class="trend-name">{trend["name"]}</div>
                <div class="trend-desc">{trend["description"]}</div>
                <img class="qr" src="data:image/png;base64,{b64}" alt="{trend['name']} QR code" />
                <br>
                <a class="watch-link" href="{trend['url']}" target="_blank">
                    ▶ Watch on {platform}
                </a>
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

# Vote confirmation
if st.session_state.voted:
    st.markdown(
        f'<div class="vote-toast">You voted for {st.session_state.voted_for}! '
        f'Thanks for making your voice heard! 🎉</div>',
        unsafe_allow_html=True,
    )

# =====================================================================
# SECTION 1 — How We Voted (always visible)
# =====================================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-head">How We Voted</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

total_votes = max(sum(votes.values()), 1)
ranked_by_votes = sorted(TRENDS, key=lambda t: votes.get(t["name"], 0), reverse=True)

for i, trend in enumerate(ranked_by_votes):
    count = votes.get(trend["name"], 0)
    pct = count / total_votes * 100
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

# =====================================================================
# SECTION 2 — Reveal the Real Rankings
# =====================================================================

st.markdown("<br><br>", unsafe_allow_html=True)

# Center the reveal button
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    if st.button(
        "🔓  Reveal the Real Rankings!" if not st.session_state.revealed else "🔓  Rankings Revealed!",
        key="reveal_btn",
        disabled=st.session_state.revealed and True,  # keep clickable only once
    ):
        st.session_state.revealed = True
        st.rerun()

if st.session_state.revealed:

    # -- Predicted ranks from votes --
    sorted_by_votes = sorted(TRENDS, key=lambda t: votes.get(t["name"], 0), reverse=True)
    predicted_ranks = {}
    for i, t in enumerate(sorted_by_votes):
        predicted_ranks[t["name"]] = i + 1

    # -- Accuracy score --
    exact_matches = sum(
        1 for t in TRENDS if predicted_ranks[t["name"]] == t["actual_rank"]
    )
    accuracy_pct = exact_matches / len(TRENDS) * 100

    # ---- Score card ----
    if accuracy_pct == 100:
        verdict = "PERFECT SCORE — y'all really know your trends! 🏆"
    elif accuracy_pct >= 60:
        verdict = "So close! Y'all have great instincts! 🔥"
    elif accuracy_pct >= 40:
        verdict = "Not bad — some of these were tricky! 💡"
    else:
        verdict = "The internet is full of surprises! 🤯"

    st.markdown(
        f"""
        <div class="score-card">
            <div class="big-number">{exact_matches}/{len(TRENDS)}</div>
            <div class="score-label">Trends ranked correctly</div>
            <div style="color:#ffffffbb; margin-top:0.8rem; font-size:1.15rem;">{verdict}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ================================================================
    # Chart 1 — Bump / Slope chart: Our Ranking vs. Actual Ranking
    # ================================================================

    st.markdown('<div class="section-head">Our Ranking vs. Reality</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    fig_bump = go.Figure()

    colors = ["#FFE293", "#FFF0C2", "#4ade80", "#60a5fa", "#f472b6"]

    for idx, trend in enumerate(TRENDS):
        pred = predicted_ranks[trend["name"]]
        actual = trend["actual_rank"]
        color = colors[idx % len(colors)]
        label = f'{trend["emoji"]} {trend["name"]}'

        fig_bump.add_trace(go.Scatter(
            x=["Our Ranking", "Actual Ranking"],
            y=[pred, actual],
            mode="lines+markers+text",
            name=label,
            text=[label, label],
            textposition=["middle left", "middle right"],
            textfont=dict(size=13, color=color, family="Nunito Sans"),
            line=dict(color=color, width=3),
            marker=dict(size=14, color=color, line=dict(width=2, color=WHITE)),
            hovertemplate=(
                f"<b>{trend['name']}</b><br>"
                f"Our rank: #{pred}<br>"
                f"Actual rank: #{actual}<br>"
                f"Real views: {format_views(trend['actual_views'])}"
                "<extra></extra>"
            ),
        ))

    fig_bump.update_layout(
        yaxis=dict(
            title="Rank", autorange="reversed", dtick=1,
            range=[0.5, len(TRENDS) + 0.5],
            gridcolor="rgba(255,255,255,0.08)", color=WHITE,
            title_font=dict(color=GOLD),
        ),
        xaxis=dict(
            color=WHITE, tickfont=dict(size=15, color=GOLD, family="Nunito Sans"),
            fixedrange=True,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito Sans", color=WHITE),
        showlegend=False,
        height=420,
        margin=dict(l=140, r=140, t=20, b=30),
        hoverlabel=dict(
            bgcolor=MAROON, font_color=GOLD, font_size=13,
            bordercolor=GOLD,
        ),
    )
    st.plotly_chart(fig_bump, use_container_width=True)

    # ================================================================
    # Chart 2 — Grouped bar: Our Vote % vs. Actual Views
    # ================================================================

    st.markdown('<div class="section-head">Vote Share vs. Actual Views</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Normalize actual views to percentages for fair comparison
    total_actual = sum(t["actual_views"] for t in TRENDS)
    names = [f'{t["emoji"]} {t["name"]}' for t in TRENDS]
    vote_pcts = [votes.get(t["name"], 0) / total_votes * 100 for t in TRENDS]
    actual_pcts = [t["actual_views"] / total_actual * 100 for t in TRENDS]

    # Sort by actual rank for a clean display
    order = sorted(range(len(TRENDS)), key=lambda i: TRENDS[i]["actual_rank"])
    names = [names[i] for i in order]
    vote_pcts = [vote_pcts[i] for i in order]
    actual_pcts = [actual_pcts[i] for i in order]
    ordered_trends = [TRENDS[i] for i in order]

    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        y=names, x=vote_pcts, orientation="h",
        name="Our Votes",
        marker=dict(color=GOLD, cornerradius=6),
        text=[f"{v:.0f}%" for v in vote_pcts],
        textposition="auto",
        textfont=dict(color=MAROON, size=13, family="Nunito Sans"),
        hovertemplate="<b>%{y}</b><br>Our vote share: %{x:.1f}%<extra></extra>",
    ))

    fig_bar.add_trace(go.Bar(
        y=names, x=actual_pcts, orientation="h",
        name="Actual Views",
        marker=dict(color="#60a5fa", cornerradius=6),
        text=[f"{v:.0f}%" for v in actual_pcts],
        textposition="auto",
        textfont=dict(color=MAROON, size=13, family="Nunito Sans"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Actual view share: %{x:.1f}%<br>"
            "Views: %{customdata}"
            "<extra></extra>"
        ),
        customdata=[format_views(ordered_trends[i]["actual_views"]) for i in range(len(ordered_trends))],
    ))

    fig_bar.update_layout(
        barmode="group",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito Sans", color=WHITE),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(size=14, color=GOLD),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title="Share (%)", color=WHITE, gridcolor="rgba(255,255,255,0.08)",
            title_font=dict(color=GOLD), range=[0, max(max(vote_pcts), max(actual_pcts)) * 1.15],
        ),
        yaxis=dict(color=WHITE, tickfont=dict(size=13)),
        height=380,
        margin=dict(l=10, r=30, t=40, b=40),
        hoverlabel=dict(bgcolor=MAROON, font_color=GOLD, font_size=13, bordercolor=GOLD),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ================================================================
    # Chart 3 — Actual view counts lollipop
    # ================================================================

    st.markdown('<div class="section-head">The Real Numbers</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    actual_sorted = sorted(TRENDS, key=lambda t: t["actual_rank"])
    lollipop_names = [f'{t["emoji"]} {t["name"]}' for t in actual_sorted]
    lollipop_views = [t["actual_views"] for t in actual_sorted]

    fig_lollipop = go.Figure()

    # stems
    for i, (name, views) in enumerate(zip(lollipop_names, lollipop_views)):
        fig_lollipop.add_trace(go.Scatter(
            x=[0, views], y=[name, name],
            mode="lines",
            line=dict(color="rgba(255,226,147,0.4)", width=3),
            showlegend=False, hoverinfo="skip",
        ))

    # dots
    fig_lollipop.add_trace(go.Scatter(
        x=lollipop_views, y=lollipop_names,
        mode="markers+text",
        marker=dict(size=18, color=GOLD, line=dict(width=2, color=WHITE)),
        text=[format_views(v) for v in lollipop_views],
        textposition="middle right",
        textfont=dict(size=14, color=GOLD_LIGHT, family="Nunito Sans"),
        showlegend=False,
        hovertemplate="<b>%{y}</b><br>Views: %{x:,.0f}<extra></extra>",
    ))

    fig_lollipop.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito Sans", color=WHITE),
        xaxis=dict(
            title="Total Views", color=WHITE,
            gridcolor="rgba(255,255,255,0.08)",
            title_font=dict(color=GOLD),
        ),
        yaxis=dict(color=WHITE, tickfont=dict(size=14), autorange="reversed"),
        height=350,
        margin=dict(l=10, r=80, t=10, b=40),
        hoverlabel=dict(bgcolor=MAROON, font_color=GOLD, font_size=13, bordercolor=GOLD),
    )
    st.plotly_chart(fig_lollipop, use_container_width=True)

    # ---- Per-trend accuracy breakdown ----
    st.markdown('<div class="section-head">Trend-by-Trend Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    breakdown_cols = st.columns(len(TRENDS))
    for col, trend in zip(breakdown_cols, sorted(TRENDS, key=lambda t: t["actual_rank"])):
        pred = predicted_ranks[trend["name"]]
        actual = trend["actual_rank"]
        diff = abs(pred - actual)

        if diff == 0:
            badge = '<span class="match-perfect">Exact match!</span>'
            icon = "🎯"
        elif diff == 1:
            badge = '<span class="match-close">Off by 1</span>'
            icon = "🔥"
        else:
            badge = f'<span class="match-off">Off by {diff}</span>'
            icon = "😮"

        with col:
            st.markdown(
                f"""
                <div class="trend-card" style="padding:1.2rem 0.8rem;">
                    <div style="font-size:2rem;">{icon}</div>
                    <div class="trend-name" style="font-size:1.1rem;">{trend["emoji"]} {trend["name"]}</div>
                    <div style="color:#ffffffbb; font-size:0.85rem; margin:0.4rem 0;">
                        We said: <b style="color:{GOLD}">#{pred}</b><br>
                        Actually: <b style="color:#60a5fa">#{actual}</b><br>
                        Views: <b style="color:{GOLD_LIGHT}">{format_views(trend["actual_views"])}</b>
                    </div>
                    {badge}
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
        #BGISS2026 &nbsp;·&nbsp; #MMCSTEAMSUMMIT &nbsp;·&nbsp;
        Scan the QR codes or tap the links to watch each trend!
    </div>
    """,
    unsafe_allow_html=True,
)
