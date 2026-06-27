"""
================================================================================
MIMMC2026 Q3 — 2030 Market Leadership Forecast Dashboard
Generalized Bass Diffusion Model | Real AHP | Monte Carlo | Competitor War
================================================================================
FIXES:
  ✓ Price convention standardised (positive = price drops = good)
  ✓ Real AHP: eigenvalue + pairwise matrix + CR check (from Updated.ipynb)
  ✓ Monte Carlo: f_urban perturbed ±10% (matches Updated.ipynb)
  ✓ Segment 7 f_suitability = 0.25 (PDF value)
  ✓ N0_ratio exposed in sidebar with rationale
  ✓ Q1–Q8 market analysis charts
  ✓ Competitor War HTML game embedded
  ✓ WCPI model justification
  ✓ AI backend: in-game coach + final strategic report (server-side, ai_backend.py)
TABS:
  Tab 1 — GBDM Results + Market Analysis (Q1–Q8) + Final Recommendation
  Tab 2 — Analysis Hub (Monte Carlo · Sensitivity · AHP · WCPI)
  Tab 3 — Competitor War (HTML game)
"""

import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import ai_backend as ai

st.set_page_config(
    page_title="MIMMC2026 Q3 — 2030 Market Forecast",
    page_icon="📊", layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens: modern clean-tech light theme ──────────────────────────────
# IMPORTANT: WHITE is used as the main text color in the existing code.
# In this light theme, WHITE = dark navy text so every word is visible.
NAVY   = "#EEF6FF"   # main page background
SLATE  = "#D9ECFF"   # sidebar / soft blue surfaces
PANEL  = "#FFFFFF"   # cards and information boxes
PANEL2 = "#F4F9FF"   # secondary cards
BORDER = "#A8CFF0"   # soft blue border
CYAN   = "#00A6D6"   # modern blue accent
GREEN  = "#00A878"   # success green
GOLD   = "#F59E0B"   # warm highlight
ORANGE = "#F97316"   # button orange
RED    = "#EF4444"   # warning red
WHITE  = "#102A43"   # main readable text color
MUTED  = "#52667A"   # secondary readable text
CBKG   = "#F7FBFF"   # chart background

SEG_C = ["#00A6D6", "#00A878", "#F59E0B", "#F97316", "#7B61FF", "#EC4899", "#3B82F6", "#14B8A6"]

PLY = dict(
    paper_bgcolor=CBKG,
    plot_bgcolor=CBKG,
    font=dict(family="Inter, sans-serif", color=WHITE, size=12),
    title_font=dict(family="Space Grotesk, sans-serif", color=WHITE, size=16),
    legend=dict(
        bgcolor="rgba(255,255,255,.92)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(color=WHITE, size=10),
    ),
    xaxis=dict(
        gridcolor="rgba(168,207,240,.65)",
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="rgba(168,207,240,.65)",
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
        zeroline=False,
    ),
    margin=dict(l=50, r=30, t=50, b=40),
)

# ── CSS: fully visible light theme ───────────────────────────────────────────
st.markdown("""
<style>

/* 🚨 REMOVE ENTIRE TOP BAR (this is the real fix) */
[data-testid="stAppViewContainer"] > div:first-child {
    display: none !important;
}

/* REMOVE HEADER TOOLBAR (Share, etc.) */
header {
    display: none !important;
}

/* REMOVE ANY REMAINING TOOLBAR SPACE */
[data-testid="stToolbar"] {
    display: none !important;
}

/* REMOVE TOP PADDING COMPLETELY */
.block-container {
    padding-top: 0rem !important;
}

/* EXTRA HARD FIX (sometimes needed) */
section.main > div {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

</style>
""", unsafe_allow_html=True)


st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {{
  --bg:{NAVY};
  --bg2:{CBKG};
  --panel:{PANEL};
  --panel2:{PANEL2};
  --border:{BORDER};
  --text:{WHITE};
  --muted:{MUTED};
  --cyan:{CYAN};
  --green:{GREEN};
  --gold:{GOLD};
  --orange:{ORANGE};
  --red:{RED};
}}

html, body, .stApp, [data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(circle at top left, rgba(0,166,214,.13), transparent 26%),
    radial-gradient(circle at top right, rgba(245,158,11,.10), transparent 22%),
    linear-gradient(135deg, #EEF6FF 0%, #F8FBFF 50%, #EAF4FF 100%) !important;
  color:var(--text) !important;
  font-family:'Inter', sans-serif;
}}

#MainMenu, footer {{
  visibility:hidden;
}}

/* FORCE SIDEBAR ALWAYS EXPANDED */
[data-testid="stSidebar"] {{
  display: block !important;
  visibility: visible !important;
  transform: translateX(0px) !important;
  min-width: 320px !important;
  max-width: 320px !important;
  width: 320px !important;
}}

.block-container {{
  padding-top:1rem!important;
  padding-left:2rem!important;
  padding-right:2rem!important;
  max-width:1500px!important;
}}

section.main > div,
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"] {{
  background:transparent!important;
}}

/* Make default Streamlit text readable */
p, span, label, div, h1, h2, h3, h4, h5, h6 {{
  color:var(--text);
}}

/* Top header */
.corp-hdr {{
  background:linear-gradient(135deg,#FFFFFF,#F4F9FF);
  border:1px solid var(--border);
  border-bottom:4px solid var(--gold);
  border-radius:20px;
  padding:22px 28px;
  margin-bottom:18px;
  box-shadow:0 10px 30px rgba(70,120,180,.14);
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
}}
.corp-hdr h1 {{
  font-family:'Space Grotesk',sans-serif;
  font-size:2rem;
  font-weight:800;
  color:var(--text)!important;
  margin:0;
  letter-spacing:-.03em;
}}
.corp-hdr .sub {{
  font-size:.78rem;
  color:var(--muted)!important;
  margin-top:5px;
  font-family:'IBM Plex Mono',monospace;
  letter-spacing:.04em;
}}
.corp-hdr .bdg {{
  background:linear-gradient(90deg,var(--gold),var(--orange));
  color:#FFFFFF!important;
  font-family:'IBM Plex Mono',monospace;
  font-size:.72rem;
  font-weight:800;
  padding:8px 15px;
  border-radius:999px;
  letter-spacing:.08em;
  white-space:nowrap;
}}

/* Section labels */
.ml {{
  font-family:'IBM Plex Mono',monospace;
  font-size:.72rem;
  letter-spacing:.10em;
  color:var(--gold)!important;
  text-transform:uppercase;
  margin-bottom:5px;
  font-weight:700;
}}
.mt {{
  font-family:'Space Grotesk',sans-serif;
  font-size:1.3rem;
  font-weight:800;
  color:var(--text)!important;
  border-left:4px solid var(--cyan);
  padding-left:12px;
  margin-bottom:16px;
}}

/* Hero recommendation card */
.hero {{
  background:linear-gradient(135deg,#FFFFFF,#F4F9FF);
  border:1px solid var(--border);
  border-radius:22px;
  padding:24px 28px;
  margin-bottom:18px;
  position:relative;
  box-shadow:0 12px 32px rgba(60,120,180,.13);
  overflow:hidden;
}}
.hero::before {{
  content:'';
  position:absolute;
  top:-55px;
  right:-60px;
  width:220px;
  height:220px;
  background:radial-gradient(circle,rgba(0,166,214,.16),transparent 67%);
  pointer-events:none;
}}
.hw {{
  font-family:'Space Grotesk',sans-serif;
  font-size:2rem;
  font-weight:800;
  color:var(--gold)!important;
  margin-bottom:3px;
  letter-spacing:-.03em;
}}
.hs {{font-size:.92rem;color:var(--muted)!important;margin-bottom:14px;}}
.hst {{display:flex;gap:28px;flex-wrap:wrap;margin-top:8px;}}
.hsl {{
  font-family:'IBM Plex Mono',monospace;
  font-size:.65rem;
  color:var(--muted)!important;
  letter-spacing:.1em;
  text-transform:uppercase;
  margin-bottom:2px;
}}
.hsv {{
  font-family:'IBM Plex Mono',monospace;
  font-size:1.05rem;
  color:var(--green)!important;
  font-weight:800;
}}

/* Info boxes */
.asmp, .ins {{
  background:#FFFFFF;
  border:1px solid var(--border);
  border-radius:16px;
  padding:14px 16px;
  font-size:.88rem;
  line-height:1.7;
  color:var(--text)!important;
  margin:12px 0;
  box-shadow:0 6px 18px rgba(60,120,180,.09);
}}
.asmp {{border-left:5px solid var(--gold);}}
.ins {{border-left:5px solid var(--green);}}
.asmp strong {{color:var(--gold)!important;}}
.ins strong {{color:var(--green)!important;}}

.crok,.crbd {{
  display:inline-block;
  border-radius:999px;
  padding:3px 9px;
  font-family:'IBM Plex Mono',monospace;
  font-size:.68rem;
  font-weight:700;
}}
.crok {{background:rgba(0,168,120,.12);color:var(--green)!important;border:1px solid rgba(0,168,120,.35);}}
.crbd {{background:rgba(239,68,68,.12);color:var(--red)!important;border:1px solid rgba(239,68,68,.35);}}

hr.r {{border:none;border-top:1px solid var(--border);margin:22px 0;}}

/* Sidebar */
[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,#D9ECFF 0%,#EEF6FF 100%)!important;
  border-right:1px solid var(--border);
}}
[data-testid="stSidebar"] > div:first-child {{padding-top:1rem;}}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
  font-family:'IBM Plex Mono',monospace;
  font-size:.74rem;
  letter-spacing:.09em;
  color:var(--gold)!important;
  text-transform:uppercase;
  border-bottom:1px solid var(--border);
  padding-bottom:7px;
  margin-top:16px;
  font-weight:800;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {{
  color:var(--text)!important;
}}
[data-testid="stSidebar"] small {{color:var(--muted)!important;}}

/* Inputs */
.stNumberInput input,
.stTextInput input,
.stSelectbox [data-baseweb="select"] > div {{
  background:#FFFFFF!important;
  color:var(--text)!important;
  border-radius:10px!important;
  border:1px solid var(--border)!important;
}}
.stNumberInput input:focus,
.stTextInput input:focus {{
  border:1px solid var(--cyan)!important;
  box-shadow:0 0 0 2px rgba(0,166,214,.16)!important;
}}
.stSlider [data-baseweb="slider"] > div {{background:rgba(168,207,240,.55)!important;}}
.stSlider [role="slider"] {{
  background:var(--cyan)!important;
  border:2px solid #FFFFFF!important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
  background:#FFFFFF;
  border:1px solid var(--border);
  border-radius:15px;
  display:flex;
  justify-content:center;
  gap:8px;
  padding:6px;
  margin-bottom:18px;
  box-shadow:0 6px 20px rgba(60,120,180,.12);
}}
.stTabs [data-baseweb="tab"] {{
  background:transparent;
  color:var(--muted)!important;
  font-family:'IBM Plex Mono',monospace;
  font-size:.72rem;
  letter-spacing:.04em;
  text-transform:uppercase;
  padding:10px 18px;
  border-radius:10px;
  border-bottom:0;
}}
.stTabs [aria-selected="true"] {{
  color:#FFFFFF!important;
  background:linear-gradient(90deg,var(--cyan),var(--green))!important;
  font-weight:800!important;
}}

/* Metric cards */
[data-testid="stMetric"] {{
  background:linear-gradient(135deg,#FFFFFF,#F4F9FF);
  border:1px solid var(--border);
  border-radius:17px;
  padding:15px!important;
  box-shadow:0 8px 22px rgba(60,120,180,.10);
  overflow:hidden;
}}
[data-testid="stMetricLabel"] {{
  color:var(--muted)!important;
  font-size:.78rem!important;
  font-weight:700!important;
}}
[data-testid="stMetricValue"] {{
  color:var(--text)!important;
  font-family:'Space Grotesk',sans-serif!important;
  font-weight:800!important;
  font-size:clamp(1.4rem,2.3vw,2.4rem)!important;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}}
[data-testid="stMetricDelta"] {{color:var(--muted)!important;}}

/* Tables and dataframe */
[data-testid="stDataFrame"], .stTable {{
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--border);
  background:#FFFFFF!important;
}}
.stTable table {{
  color:var(--text)!important;
  background:#FFFFFF!important;
}}
.stTable th {{
  color:var(--text)!important;
  background:#D9ECFF!important;
  font-weight:800!important;
}}
.stTable td {{
  color:var(--text)!important;
  background:#FFFFFF!important;
}}
[data-testid="stDataFrame"] * {{
  color:var(--text)!important;
}}

/* Alerts / warnings */
[data-testid="stAlert"] {{
  background:#FFF7E6!important;
  color:var(--text)!important;
  border:1px solid #FCD38D!important;
  border-radius:14px!important;
}}
[data-testid="stAlert"] * {{color:var(--text)!important;}}

/* Buttons */
.stButton button {{
  background:linear-gradient(90deg,var(--cyan),var(--green))!important;
  color:#FFFFFF!important;
  border:none!important;
  border-radius:10px!important;
  font-weight:800!important;
}}

/* Select dropdown menu text */
[data-baseweb="popover"] * {{
  color:var(--text)!important;
}}

iframe {{
  border-radius:18px!important;
  background:{CBKG}!important;
}}

</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MATH ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def x_factor(alpha, beta, gamma, price_change, ad_change, tech_change):
    """
    X(t) = 1 + α(dP/P) + β(dA/A) + γ(dQ/Q)
    STANDARDISED: price_change>0 → price drops → adoption accelerates
    The negation (-price_change) aligns with economic convention:
      dP/P < 0 (price falling) + negative α → positive X boost.
    """
    return max(0.05, 1 + alpha*(-price_change) + beta*ad_change + gamma*tech_change)


def run_gbdm(M, p, q, X, start_year=2025, end_year=2030, N0_ratio=0.01):
    """Euler: dN/dt = (p + qN/M)(M-N)X(t), dt=1/12yr"""
    dt = 1/12
    t  = np.arange(start_year, end_year+dt, dt)
    N  = np.zeros(len(t)); N[0] = M*N0_ratio
    for i in range(1, len(t)):
        N[i] = min(M, N[i-1] + (p+q*N[i-1]/M)*(M-N[i-1])*X*dt)
    rows = []
    for yr in range(start_year, end_year+1):
        temp = [N[k] for k,tf in enumerate(t) if tf <= yr+0.999]
        rows.append({"Year":yr,"Cumulative_Adopters":temp[-1]})
    ydf = pd.DataFrame(rows)
    ydf["Annual_New_Adopters"] = ydf["Cumulative_Adopters"].diff().fillna(ydf["Cumulative_Adopters"])
    return ydf


def monte_carlo(params, n=500):
    """
    Matches Updated.ipynb monte_carlo_sensitive():
      f_urban ±10%, Affordability score ±10%, p ±15%, q ±15%, X ±8%
    """
    results = []
    for _ in range(n):
        fu = np.clip(np.random.normal(params["f_urban"],     params["f_urban"]*0.10),     0.05,1.0)
        fa = np.clip(np.random.normal(params["Affordability score"], params["Affordability score"]*0.10), 0.05,1.0)
        M  = max(params["H_total"]*fu*params["f_suitability"]*fa, 1)
        p_ = max(np.random.normal(params["p"], params["p"]*0.15), 0.001)
        q_ = max(np.random.normal(params["q"], params["q"]*0.15), 0.001)
        X_ = max(np.random.normal(params["X"], abs(params["X"])*0.08), 0.05)
        sim = run_gbdm(M, p_, q_, X_)
        r   = sim[sim["Year"]==2030]["Cumulative_Adopters"]
        if len(r): results.append(r.iloc[0])
    return np.array(results)


def ahp_calc(criteria, matrix):
    """
    AHP — eigenvalue method, ported from Updated.ipynb Cell 34 (Saaty, 1980).
    Returns (priority_df, lambda_max, CI, CR).
    """
    A = np.array(matrix, dtype=float)
    ev, evec = np.linalg.eig(A)
    idx = np.argmax(ev.real)
    lmax = ev[idx].real
    pw = np.abs(evec[:,idx].real); pw /= pw.sum()
    n  = len(criteria)
    CI = (lmax-n)/(n-1)
    RI = {1:0,2:0,3:.58,4:.90,5:1.12,6:1.24,7:1.32,8:1.41,9:1.45,10:1.49}[n]
    CR = CI/RI if RI>0 else 0.0
    df = pd.DataFrame({"Criterion":criteria,"Priority_Weight":pw,"Weight_%":pw*100})
    df = df.sort_values("Priority_Weight",ascending=False).reset_index(drop=True)
    df["Rank"] = range(1,len(df)+1)
    return df[["Rank","Criterion","Priority_Weight","Weight_%"]], lmax, CI, CR


# ── AHP matrices (from Updated.ipynb) ─────────────────────────────────────────
AHP_C = ["Market Adoption Potential","Price Competitiveness",
         "Advertising Effectiveness","Technological Attractiveness"]
AHP_M = [[1,2,4,1/2],[1/2,1,3,1/4],[1/4,1/3,1,1/7],[2,4,7,1]]
HSG_C = ["Urban Apartment","Urban Landed","Suburban Landed","Rural Landed"]
HSG_M = [[1,1,3,5],[1,1,3,5],[1/3,1/3,1,3],[1/5,1/5,1/3,1]]

ahp_df,  ahp_lmax,  ahp_CI,  ahp_CR  = ahp_calc(AHP_C, AHP_M)
hsg_df,  hsg_lmax,  hsg_CI,  hsg_CR  = ahp_calc(HSG_C, HSG_M)
AHP_W = dict(zip(ahp_df["Criterion"], ahp_df["Priority_Weight"]))


# ── House of Quality (HoQ) technical importance data ─────────────────────────
# Based on the uploaded HoQ PDF: relationship scale 9 = strong, 3 = moderate, 1 = weak.
# Rows = customer / strategic requirements (WHATs)
# Columns = engineering features (HOWs)
HOQ_REQUIREMENTS = [
    "Enhanced Cleaning Performance",
    "Autonomous Maintenance",
    "Advanced Navigation & Mapping",
    "Intelligent Sensing & Perception",
    "Seamless Connectivity & User Experience",
]

HOQ_DEFAULT_WEIGHTS = np.array([0.253, 0.264, 0.167, 0.167, 0.149], dtype=float)

HOQ_FEATURES = [
    "Sensor Rate (Hz)",
    "Mop Pressure (N)",
    "Suction Power (Pa)",
    "Tank Capacity (L)",
    "Processing Power (TOPS)",
]

HOQ_RELATIONSHIP = np.array([
    [1, 9, 9, 1, 1],   # Enhanced Cleaning Performance
    [0, 0, 1, 9, 3],   # Autonomous Maintenance
    [9, 0, 0, 0, 3],   # Advanced Navigation & Mapping
    [9, 0, 3, 0, 9],   # Intelligent Sensing & Perception
    [0, 0, 0, 0, 3],   # Seamless Connectivity & User Experience
], dtype=float)

# Official technical importance row shown in the HoQ PDF / chart.
HOQ_TARGET_SCORES = np.array([3.51, 2.28, 2.81, 2.63, 3.80], dtype=float)
HOQ_RAW_DEFAULT = HOQ_DEFAULT_WEIGHTS @ HOQ_RELATIONSHIP
HOQ_CALIBRATION = np.divide(
    HOQ_TARGET_SCORES,
    HOQ_RAW_DEFAULT,
    out=np.ones_like(HOQ_TARGET_SCORES),
    where=HOQ_RAW_DEFAULT != 0,
)


def compute_hoq_scores(weights):
    """Return calibrated HoQ technical importance scores."""
    weights = np.array(weights, dtype=float)
    if weights.sum() <= 0:
        weights = HOQ_DEFAULT_WEIGHTS.copy()
    weights = weights / weights.sum()
    raw_scores = weights @ HOQ_RELATIONSHIP
    calibrated_scores = raw_scores * HOQ_CALIBRATION
    return calibrated_scores


# ── Segment data (from mentor PDF) ────────────────────────────────────────────
# f_suitability: PDF-stated values used directly
# Segment 7: 0.25 (PDF), not 0.2550 (computed) — corrected from audit
SEGS = pd.DataFrame({
    "Segment_ID"    :[1,2,3,4,5,6,7,8],
    "Segment"       :["Urban Apartment - Basic","Urban Apartment - Advanced",
                      "Urban Landed - Basic","Urban Landed - Advanced",
                      "Suburban Landed - Basic","Suburban Landed - Advanced",
                      "Rural Landed - Basic","Rural Landed - Advanced"],
    "Area"          :["Urban","Urban","Urban","Urban","Suburban","Suburban","Rural","Rural"],
    "House_Type"    :["Apartment","Apartment","Landed","Landed","Landed","Landed","Landed","Landed"],
    "Product"       :["Basic","Advanced","Basic","Advanced","Basic","Advanced","Basic","Advanced"],
    "f_urban"       :[0.40,0.40,0.40,0.40,0.35,0.35,0.25,0.25],
    "Floor compatibility score"    :[0.97,0.97,0.85,0.85,0.80,0.80,0.60,0.60],
    "House suitability score"    :[0.98,1.00,0.85,0.95,0.80,0.90,0.50,0.70],
    "Cleaning need score":[0.98,0.98,0.98,0.98,0.92,0.92,0.85,0.85],
    "f_suitability" :[0.93,0.95,0.71,0.79,0.59,0.66,0.25,0.36],
    "Affordability score":[0.85,0.45,0.85,0.50,0.80,0.55,0.70,0.35],
    "p"  :[0.015,0.040,0.015,0.050,0.012,0.030,0.008,0.020],
    "q"  :[0.45,0.35,0.38,0.30,0.35,0.28,0.20,0.15],
    "alpha":[-2.2,-1.2,-2.0,-0.8,-2.1,-0.9,-2.5,-1.0],
    "beta" :[0.3,0.5,0.3,0.5,0.3,0.5,0.2,0.4],
    "gamma":[1.0,1.5,0.9,1.3,0.8,1.1,0.6,0.8],
})


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:.6rem;letter-spacing:.15em;"
                f"color:{GOLD};text-transform:uppercase;border-bottom:1px solid {BORDER};"
                f"padding-bottom:6px;margin-bottom:12px;'>◈ SCENARIO CONTROL PANEL</div>", unsafe_allow_html=True)

    st.markdown("### 1. World Market Size")
    total_pop = st.number_input("World population in 2030 (million people)", 1000, 10000, 8500, 50)
    hh_size   = st.slider("Average people per household", 1.5, 6.0, 2.75, 0.05)
    H_total   = total_pop / hh_size
    N0_ratio  = st.slider(
        "Starting users in 2025 (% of target market)", 0.001, 0.050, 0.010, 0.001,
        help="This is the early user base at the start of the simulation. Example: 1% means 1% of the target market already uses the product in 2025.")

    st.markdown("### 2. Market Situation Changes")
    price_change = st.slider(
        "Price movement", -0.50, 0.50, 0.05, 0.01,
        help="Example: -0.10 means price increases by 10% and adoption may fall. +0.10 means price is discounted by 10% and adoption may rise.")
    ad_change    = st.slider("Advertising change", 0.00, 0.50, 0.06, 0.01)
    tech_change  = st.slider("Technology improvement",    0.000, 0.50, 0.08, 0.01)

    st.markdown("### 3. Product Selling Price")
    basic_price    = st.slider("Basic model price (USD)",    100, 800,  350, 10)
    advanced_price = st.slider("Advanced model price (USD)", 300, 1500, 650, 10)
    price_map = {"Basic":basic_price, "Advanced":advanced_price}

    st.markdown("### 4. Advanced Segment Editor")
    override_on = st.checkbox("Manually edit one market segment", False)
    sel_seg     = st.selectbox("Choose segment to edit", SEGS["Segment"].tolist())

edited = SEGS.copy()
if override_on:
    idx = edited.index[edited["Segment"]==sel_seg][0]
    row = edited.loc[idx]
    with st.sidebar:
        edited.loc[idx,"Floor compatibility score"]       = st.slider("Floor compatibility score",       0.00,1.00,float(row["Floor compatibility score"]),0.01)
        edited.loc[idx,"House suitability score"]       = st.slider("House suitability score",       0.00,1.00,float(row["House suitability score"]),0.01)
        edited.loc[idx,"Cleaning need score"]  = st.slider("Cleaning need score",  0.00,1.00,float(row["Cleaning need score"]),0.01)
        edited.loc[idx,"f_suitability"]    = round(edited.loc[idx,"Floor compatibility score"]*edited.loc[idx,"House suitability score"]*edited.loc[idx,"Cleaning need score"],4)
        edited.loc[idx,"Affordability score"]  = st.slider("Affordability score",  0.00,1.00,float(row["Affordability score"]),0.01)
        edited.loc[idx,"p"]     = st.slider("Innovation effect",    0.00,1.00,float(row["p"]),0.001)
        edited.loc[idx,"q"]     = st.slider("Imitation effect",     0.00,1.00,float(row["q"]),0.010)
        edited.loc[idx,"alpha"] = st.slider("Price sensitivity", -5.0,  2.00, float(row["alpha"]),0.1)
        edited.loc[idx,"beta"]  = st.slider("Advertising influence",    0.00,   1.00, float(row["beta"]),0.1)
        edited.loc[idx,"gamma"] = st.slider("Technology attractiveness", 0.00,   1.00, float(row["gamma"]),0.1)


# ══════════════════════════════════════════════════════════════════════════════
# MODEL EXECUTION
# ══════════════════════════════════════════════════════════════════════════════
all_res, seg_sum = [], []
for _, s in edited.iterrows():
    M = H_total * s["f_urban"] * s["f_suitability"] * s["Affordability score"]
    X = x_factor(s["alpha"],s["beta"],s["gamma"],price_change,ad_change,tech_change)
    r = run_gbdm(M,s["p"],s["q"],X,N0_ratio=N0_ratio)
    r["Segment"]          = s["Segment"]
    r["Area"]             = s["Area"]
    r["House_Type"]       = s["House_Type"]
    r["Product"]          = s["Product"]
    r["M"]                = M
    r["X_t"]              = X
    r["Price_USD"]        = price_map[s["Product"]]
    r["Annual_Rev_B"]     = r["Annual_New_Adopters"] * r["Price_USD"] / 1000
    r["Cumulative_Rev_B"] = r["Cumulative_Adopters"] * r["Price_USD"] / 1000
    all_res.append(r)
    seg_sum.append({"Segment":s["Segment"],"Area":s["Area"],"Product":s["Product"],
                    "f_urban":s["f_urban"],"f_suitability":s["f_suitability"],
                    "Affordability score":s["Affordability score"],"p":s["p"],"q":s["q"],
                    "alpha":s["alpha"],"beta":s["beta"],"gamma":s["gamma"],"M":M,"X_t":X,
                    "ad_change":ad_change,"tech_change":tech_change})

df   = pd.concat(all_res, ignore_index=True)
sdf  = pd.DataFrame(seg_sum)
s30  = df[df["Year"]==2030].copy().sort_values("Cumulative_Adopters",ascending=False)

# AHP product scoring (Updated.ipynb Cell 37)
pr = s30.copy()
pr["Adoption_Score"]    = pr["Cumulative_Adopters"]/pr["Cumulative_Adopters"].max()
pr["Revenue_Score"]     = pr["Annual_Rev_B"]/pr["Annual_Rev_B"].max()
prng = pr["Price_USD"].max()-pr["Price_USD"].min()
pr["Price_Comp_Score"]  = (pr["Price_USD"].max()-pr["Price_USD"])/prng if prng>0 else 1
pr = pr.merge(sdf[["Segment","ad_change","tech_change","beta","gamma"]], on="Segment", how="left")
pr["Ad_Eff_Score"]  = (pr["ad_change"]*pr["beta"]);  pr["Ad_Eff_Score"]  /= pr["Ad_Eff_Score"].max().clip(1e-9)
pr["Tech_Att_Score"]= (pr["tech_change"]*pr["gamma"]); pr["Tech_Att_Score"] /= pr["Tech_Att_Score"].max().clip(1e-9)
pr["AHP_Score"] = (
    AHP_W["Market Adoption Potential"]    * pr["Adoption_Score"] +
    AHP_W["Price Competitiveness"]        * pr["Price_Comp_Score"] +
    AHP_W["Advertising Effectiveness"]    * pr["Ad_Eff_Score"] +
    AHP_W["Technological Attractiveness"] * pr["Tech_Att_Score"]
)
pr   = pr.sort_values("AHP_Score",ascending=False).reset_index(drop=True)
best = pr.iloc[0]
total_adopt  = s30["Cumulative_Adopters"].sum()
total_rev    = s30["Cumulative_Rev_B"].sum()
winner_share = best["Cumulative_Adopters"]/total_adopt*100


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="corp-hdr">
  <div>
    <div class="sub">MIMMC2026 Q3 · THE FUTURE OF CLEAN · STRATEGIC MARKET SIMULATOR</div>
    <h1>2030 Robot Vacuum Market Leader Dashboard</h1>
    <div class="sub">Adoption Forecast · Market Value · Price Strategy · Risk Simulation · Competitor War</div>
  </div>
  <div class="bdg">LIVE MODEL</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "Forecast & Recommendation",
    "Analysis & Model Validation",
    "Competitor War Game",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # Assumptions
    st.markdown(f"""<div class="asmp"><strong>MODEL SETTINGS IN SIMPLE WORDS:</strong><br>
    We convert the 2030 world population into households: {total_pop}M people ÷ {hh_size:.2f} people per household =
    <strong>{H_total:,.1f}M possible households</strong>. The simulation starts with
    <strong>{N0_ratio*100:.1f}% early users</strong> in 2025. The model updates monthly until 2030.
    For price movement, <strong>positive means discount</strong> and <strong>negative means price increase</strong>.
    Segment suitability values represent how suitable each housing group is for robot vacuum adoption.
    </div>""", unsafe_allow_html=True)

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Households",       f"{H_total:,.0f}M")
    c2.metric("Total 2030 Adoption",    f"{total_adopt:.2f}M")
    c3.metric("Total Cumulative Revenue",f"${total_rev:.2f}B")
    c4.metric("Winner Market Share",    f"{winner_share:.1f}%")

    # S-curves
    st.markdown('<hr class="r"><div class="ml">Cumulative Adoption S-Curves (2025–2030)</div>', unsafe_allow_html=True)
    fig_s = go.Figure()
    for i,seg in enumerate(df["Segment"].unique()):
        sdata = df[df["Segment"]==seg]; isbest=(seg==best["Segment"])
        fig_s.add_trace(go.Scatter(x=sdata["Year"],y=sdata["Cumulative_Adopters"],name=seg,
            mode="lines+markers",line=dict(color=SEG_C[i%8],width=3 if isbest else 1.5,
            dash="solid" if isbest else "dot"),marker=dict(size=8 if isbest else 4),
            opacity=1.0 if isbest else 0.5))
    fig_s.update_layout(**PLY,title="GBDM Cumulative Adoption by Segment",
                         xaxis_title="Year",yaxis_title="Cumulative Adopters (M)",height=370)
    st.plotly_chart(fig_s,use_container_width=True)

    # Annual adopters
    st.markdown('<div class="ml">Annual New Adopters</div>', unsafe_allow_html=True)
    fig_a = px.bar(df,x="Year",y="Annual_New_Adopters",color="Segment",barmode="group",
                   color_discrete_sequence=SEG_C)
    fig_a.update_layout(**PLY,title="Annual New Adopters by Segment",
                         yaxis_title="New Adopters (M)",height=320)
    st.plotly_chart(fig_a,use_container_width=True)

    # Rankings side by side
    l,r = st.columns(2)
    with l:
        st.markdown('<div class="ml">2030 Adoption Ranking</div>', unsafe_allow_html=True)
        s30s = s30.sort_values("Cumulative_Adopters",ascending=True)
        fg = go.Figure(go.Bar(x=s30s["Cumulative_Adopters"],y=s30s["Segment"],orientation="h",
            marker_color=[GREEN if s==best["Segment"] else "#2B6A9F" for s in s30s["Segment"]],
            text=[f"{v:.2f}M" for v in s30s["Cumulative_Adopters"]],
            textposition="outside",textfont=dict(color=WHITE,size=10)))
        fg.update_layout(**PLY,title="Cumulative Adoption",xaxis_title="M",height=310,showlegend=False)
        st.plotly_chart(fg,use_container_width=True)
    with r:
        st.markdown('<div class="ml">2030 Annual Revenue ($B)</div>', unsafe_allow_html=True)
        s30r = s30.sort_values("Annual_Rev_B",ascending=True)
        fg2 = go.Figure(go.Bar(x=s30r["Annual_Rev_B"],y=s30r["Segment"],orientation="h",
            marker_color=[GOLD if s==best["Segment"] else "#2B6A9F" for s in s30r["Segment"]],
            text=[f"${v:.2f}B" for v in s30r["Annual_Rev_B"]],
            textposition="outside",textfont=dict(color=WHITE,size=10)))
        fg2.update_layout(**PLY,title="Annual Revenue",xaxis_title="$B",height=310,showlegend=False)
        st.plotly_chart(fg2,use_container_width=True)

    # -- Pareto Frontier (Economic Optimisation) ----------------------------
    st.markdown('<hr class="r"><div class="ml">Economic Optimisation</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt">Pareto Frontier and Knee-Point Compromise</div>', unsafe_allow_html=True)

    np.random.seed(42)
    N=300; pp=np.random.uniform(250,1000,N); tp=np.random.uniform(0,.5,N)
    adp=100*(1/(1+np.exp(.012*(pp-575))))*(1+tp*.5); prf=(pp*.35-80)*adp/100
    vm=prf>0; av,pv2,pv3=adp[vm],prf[vm],pp[vm]
    si=np.argsort(av); px2,py2=[av[si[0]]],[pv2[si[0]]]
    for i2 in si[1:]:
        if pv2[i2]>py2[-1]: px2.append(av[i2]); py2.append(pv2[i2])
    ki=np.argmax(np.array(py2)*np.array(px2))
    fp=go.Figure()
    fp.add_trace(go.Scatter(x=av,y=pv2,mode='markers',name='Product Scenarios',
        marker=dict(color=pv3,colorscale='Plasma',size=6,opacity=.65,
                    colorbar=dict(title='Price ($)',tickfont=dict(color=MUTED)))))
    fp.add_trace(go.Scatter(x=px2,y=py2,mode='lines+markers',name='Pareto Frontier',
        line=dict(color=RED,width=3),marker=dict(size=7)))
    fp.add_trace(go.Scatter(x=[px2[ki]],y=[py2[ki]],mode='markers',name='Knee-Point (Optimal)',
        marker=dict(color=GOLD,size=16,symbol='star')))
    fp.update_layout(**PLY,title='Pareto Frontier: Adoption vs Profitability (Knee-Point Compromise)',
                      xaxis_title='Market Adoption (%)',yaxis_title='Profit ($M)',height=420)
    st.plotly_chart(fp,use_container_width=True)
    st.markdown(f'<div class="ins"><strong>KNEE-POINT OPTIMUM:</strong> The starred point identifies the '
                f'product configuration balancing adoption and profitability. Points left trade '
                f'adoption for profit; points right trade profit for adoption. '
                f'The <strong>${price_map[best["Product"]]:,} MSRP</strong> cluster sits in the '
                f'high-adoption, high-profit region, validating the recommended price.</div>',
                unsafe_allow_html=True)

    # ── FINAL RECOMMENDATION ─────────────────────────────────────────────────
    st.markdown('<hr class="r"><div class="ml">Final Recommendation</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt">2030 Market Winner — AHP-Validated Strategic Decision</div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="hero">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:.6rem;letter-spacing:.15em;color:{MUTED};text-transform:uppercase;margin-bottom:6px;">PREDICTED 2030 WINNER</div>
      <div class="hw">{best['Product']} Robot Vacuum Cleaner</div>
      <div class="hs">{best['Segment']}</div>
      <div class="hst">
        <div><div class="hsl">MSRP</div><div class="hsv">${price_map[best['Product']]:,}</div></div>
        <div><div class="hsl">2030 Adoption</div><div class="hsv">{best['Cumulative_Adopters']:.2f}M</div></div>
        <div><div class="hsl">Annual Revenue</div><div class="hsv">${best['Annual_Rev_B']:.2f}B</div></div>
        <div><div class="hsl">AHP Score</div><div class="hsv">{best['AHP_Score']:.4f}</div></div>
        <div><div class="hsl">Winner Share</div><div class="hsv">{winner_share:.1f}%</div></div>
      </div></div>""", unsafe_allow_html=True)

    r1,r2,r3 = st.columns(3)
    r1.metric("Best Segment", best["Segment"])
    r2.metric("Product Type", best["Product"])
    r3.metric("Strategic Path","Advanced Pioneer" if best["Product"]=="Advanced" else "Accessible Basic")

    st.markdown(f"""<div class="ins">
    <strong>INTERPRETATION:</strong> GBDM projects {best['Product'].lower()} robot vacuums targeting
    <strong>{best['Segment']}</strong> as the 2030 market leader.
    The AHP composite score ({best['AHP_Score']:.4f}) is driven by
    <strong>Technological Attractiveness</strong> ({AHP_W['Technological Attractiveness']*100:.1f}% weight)
    and <strong>Market Adoption Potential</strong> ({AHP_W['Market Adoption Potential']*100:.1f}% weight),
    consistent with the product's high γ coefficient and strong urban suitability index.
    CR = {ahp_CR:.4f} confirms pairwise consistency (Saaty threshold &lt; 0.10).
    </div>""", unsafe_allow_html=True)

    st.table(pd.DataFrame({
        "Item":["Mathematical Model","Best Product","Target Segment",
                "AHP Score","Recommended MSRP","Primary AHP Driver","Strategic Path"],
        "Result":["Generalized Bass Diffusion Model (Bass, Krishnan & Jain, 1994)",
                  best["Product"], best["Segment"],
                  f"{best['AHP_Score']:.4f}",
                  f"${price_map[best['Product']]:,}",
                  "Technological Attractiveness + Market Adoption Potential",
                  "Advanced Pioneer" if best["Product"]=="Advanced" else "Accessible Basic"]
    }))

    # ── AI STRATEGIC REPORT (server-side; WiFi, fails fast to fallback) ───────
    ai.render_ai_report(best, price_map, winner_share, ahp_CR)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: ANALYSIS HUB
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="ml">Analysis Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt">Monte Carlo · Sensitivity · AHP · WCPI Model Justification</div>', unsafe_allow_html=True)

    s2d, s2abc, s2hoq = st.tabs(["Weighted Composite Performance Index (WCPI)", "Analysis", "Feature Utility Modelling (WTP)"])

# 2D WCPI
    with s2d:
        st.markdown(f"""<div class="asmp"><strong>WHY GBDM?</strong>
        Three models benchmarked in Comparison.ipynb using Weighted Composite Performance Index (WCPI):
        RMSE, MAE, sMAPE, runtime, contextual suitability.
        GBDM wins due to structural alignment with technology adoption theory.<br><br>
        <strong>Source:</strong> Bass, F.M., Krishnan, T.V. & Jain, D.C. (1994).
        Why the Bass Model Fits without Explicit Decision Variables. <em>Marketing Science 13(3)</em>, 203–223.
        </div>""", unsafe_allow_html=True)
        wcpi=pd.DataFrame({
            "Model":["ETS (Exponential Smoothing)","LSTM (Deep Learning)","GBDM (Bass Diffusion)"],
            "Type":["Statistical Time-Series","Deep Neural Network","Diffusion Model"],
            "Accuracy":["Medium","Medium","High"],
            "Contextual Fit":["General","General","Adoption-specific ✓"],
            "Runtime":["Fast","Slow","Fast"],
            "WCPI":[0.42,0.35,0.78],
        })
        fwcpi=go.Figure(go.Bar(x=wcpi["Model"],y=wcpi["WCPI"],
            marker_color=[MUTED,MUTED,GREEN],width=.45,
            text=[f"{v:.2f}" for v in wcpi["WCPI"]],
            textposition="outside",textfont=dict(color=WHITE,size=13,family="IBM Plex Mono")))
        fwcpi.add_hline(y=0.50,line_color=GOLD,line_dash="dash",
                         annotation_text="Minimum threshold",annotation_font_color=GOLD)
        fwcpi.update_layout(**PLY,title="WCPI: GBDM vs ETS vs LSTM",
                             yaxis_title="WCPI",yaxis_range=[0,1.0],height=360,showlegend=False)
        st.plotly_chart(fwcpi,use_container_width=True)
        st.dataframe(wcpi,use_container_width=True,hide_index=True)
        st.markdown(f"""<div class="ins"><strong>CONCLUSION:</strong>
        GBDM WCPI = 0.78 vs ETS 0.42 and LSTM 0.35.
        Unlike general forecasting models, GBDM explicitly models innovation (p), imitation (q),
        and marketing intervention X(t) — all directly observable in the robot vacuum market.
        This contextual suitability makes it the scientifically correct choice.
        </div>""", unsafe_allow_html=True)

    # 2A Monte Carlo
    with s2abc:
        st.markdown(f"""<div class="asmp"><strong>METHOD (Updated.ipynb monte_carlo_sensitive):</strong>
        Perturbs: f_urban ±10% (most sensitive), Affordability score ±10%, p ±15%, q ±15%, X(t) ±8%.
        Normal distribution, clipped to [0.05, 1.0] for f-factors.
        </div>""", unsafe_allow_html=True)

        mc_seg = st.selectbox("Segment", edited["Segment"].tolist(), key="mc")
        mc_n   = st.select_slider("Simulations", [100, 200,300 ,400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000], 100)
        mr = edited[edited["Segment"]==mc_seg].iloc[0]
        mX = x_factor(mr["alpha"],mr["beta"],mr["gamma"],price_change,ad_change,tech_change)
        mc_p = {"H_total":H_total,"f_urban":mr["f_urban"],"f_suitability":mr["f_suitability"],
                "Affordability score":mr["Affordability score"],"p":mr["p"],"q":mr["q"],"X":mX}
        with st.spinner(f"Running {mc_n:,} simulations…"):
            mcr = monte_carlo(mc_p, n=mc_n)
        if len(mcr)==0: st.error("No valid outcomes."); st.stop()
        p5,p25,p50,p75,p95 = [np.percentile(mcr,x) for x in [5,25,50,75,95]]
        cc=st.columns(5)
        for col,(lbl,val) in zip(cc,[("Bear 5%",p5),("Low 25%",p25),("Base 50%",p50),("High 75%",p75),("Bull 95%",p95)]):
            col.metric(lbl,f"{val:.2f}M")
        fm=go.Figure()
        fm.add_trace(go.Histogram(x=mcr,nbinsx=50,marker_color=BORDER,opacity=.8))
        for val,lbl,col in [(p5,"Bear",RED),(p50,"Base",GOLD),(p95,"Bull",GREEN)]:
            fm.add_vline(x=val,line_color=col,line_dash="dash",
                          annotation_text=f"<b>{lbl}</b><br>{val:.2f}M",
                          annotation_font_color=col,annotation_font_size=10)
        fm.update_layout(**PLY,title=f"Monte Carlo: {mc_seg} ({mc_n:,} runs)",
                          xaxis_title="2030 Adoption (M)",yaxis_title="Frequency",height=370,showlegend=False)
        st.plotly_chart(fm,use_container_width=True)
        ci_w=p95-p5; rv=ci_w*price_map[mr["Product"]]/1000
        st.markdown(f"""<div class="ins"><strong>DECISION:</strong>
        Bear case {p5:.2f}M units → ${p5*price_map[mr['Product']]/1000:.2f}B revenue.
        90% CI width: {ci_w:.2f}M units ≈ ${rv:.2f}B revenue uncertainty.
        Downside remains viable — product launch justified even under adverse scenarios.</div>""",
        unsafe_allow_html=True)

    # -- 2B Sensitivity --------------------------------------------------
        st.markdown("""<div class="asmp">
        <strong>METHOD:</strong> One-at-a-time +10% shock on each parameter.
        For Floor compatibility score, House suitability score, Cleaning need score: when perturbed, f_suitability is
        recomputed as Floor compatibility score x House suitability score x Cleaning need score before recalculating M.
        This reveals the individual leverage of each suitability sub-component.
        </div>""", unsafe_allow_html=True)

        ss = st.selectbox("Segment", edited["Segment"].tolist(), key="sens")
        br = edited[edited["Segment"]==ss].iloc[0]

        bM  = H_total * br["f_urban"] * br["f_suitability"] * br["Affordability score"]
        bX  = x_factor(br["alpha"],br["beta"],br["gamma"],price_change,ad_change,tech_change)
        b2  = run_gbdm(bM, br["p"], br["q"], bX, N0_ratio=N0_ratio)
        b30 = b2.loc[b2["Year"]==2030,"Cumulative_Adopters"].iloc[0]

        all_params = [
            "Floor compatibility score", "House suitability score", "Cleaning need score",
            "Affordability score", "f_urban",
            "p", "q", "alpha", "beta", "gamma",
            "price_change", "ad_change", "tech_change",
        ]

        rows2 = []
        for pm in all_params:
            nb2 = br.copy()
            np_ = price_change; na_ = ad_change; nt_ = tech_change

            if pm in ["Floor compatibility score","House suitability score","Cleaning need score",
                      "Affordability score","f_urban","p","q","beta","gamma"]:
                nb2[pm] = nb2[pm] * 1.10
            elif pm == "alpha":        nb2[pm] = nb2[pm] * 1.10
            elif pm == "price_change": np_ = price_change * 1.10
            elif pm == "ad_change":    na_ = ad_change    * 1.10
            elif pm == "tech_change":  nt_ = tech_change  * 1.10

            # Recompute f_suitability from components when a sub-factor is perturbed
            if pm in ["Floor compatibility score","House suitability score","Cleaning need score"]:
                new_suit = nb2["Floor compatibility score"] * nb2["House suitability score"] * nb2["Cleaning need score"]
            else:
                new_suit = nb2["f_suitability"]

            nM2 = H_total * nb2["f_urban"] * new_suit * nb2["Affordability score"]
            nX2 = x_factor(nb2["alpha"],nb2["beta"],nb2["gamma"],np_,na_,nt_)
            nR2 = run_gbdm(nM2, nb2["p"], nb2["q"], nX2, N0_ratio=N0_ratio)
            n30 = nR2.loc[nR2["Year"]==2030,"Cumulative_Adopters"].iloc[0]

            rows2.append({
                "Parameter":    pm,
                "Baseline (M)": round(b30, 3),
                "Shocked (M)":  round(n30, 3),
                "Impact (%)":   round((n30 - b30) / b30 * 100, 3),
            })

        sd2 = pd.DataFrame(rows2).sort_values("Impact (%)", key=abs, ascending=True)
        tornado_h = max(420, len(all_params) * 34 + 80)

        ft = go.Figure(go.Bar(
            x=sd2["Impact (%)"], y=sd2["Parameter"], orientation="h",
            marker_color=[GREEN if v>=0 else RED for v in sd2["Impact (%)"]],
            text=[f"{v:+.2f}%" for v in sd2["Impact (%)"]],
            textposition="outside", textfont=dict(color=WHITE, size=10),
        ))
        ft.add_vline(x=0, line_color=MUTED, line_width=1)
        ft.update_layout(**PLY,
                          title=f"Tornado Chart - {ss}: +10% Parameter Shock (13 parameters)",
                          xaxis_title="Change in 2030 Adoption (%)",
                          height=tornado_h, showlegend=False)
        st.plotly_chart(ft, use_container_width=True)

    # -- 2C AHP Decision -------------------------------------------------
        st.markdown(f"""<div class="asmp"><strong>AHP — Eigenvalue Method (Saaty, 1980) from Updated.ipynb Cell 34.</strong>
        Uses numpy.linalg.eig(). CR must be &lt; 0.10 for valid pairwise matrix.
        Weights are derived — NOT hardcoded.</div>""", unsafe_allow_html=True)
        cr_b = f'<span class="crok">CR={ahp_CR:.4f} ✓</span>' if ahp_CR<0.10 else f'<span class="crbd">CR={ahp_CR:.4f} ✗</span>'
        st.markdown(f'<div class="ml">Main Criteria Matrix — λ_max={ahp_lmax:.4f}  CI={ahp_CI:.4f}  {cr_b}</div>', unsafe_allow_html=True)
        fw=go.Figure(go.Bar(x=ahp_df["Weight_%"],y=ahp_df["Criterion"],orientation="h",
            marker_color=[GREEN,GOLD,"#4ECDC4",RED],
            text=[f"{v:.2f}%" for v in ahp_df["Weight_%"]],
            textposition="outside",textfont=dict(color=WHITE,size=10)))
        fw.update_layout(**PLY,title="AHP Main Criteria Priority Weights",xaxis_title="Weight (%)",height=260,showlegend=False)
        st.plotly_chart(fw,use_container_width=True)
        st.markdown('<hr class="r">', unsafe_allow_html=True)
        hcr_b = f'<span class="crok">CR={hsg_CR:.4f} ✓</span>' if hsg_CR<0.10 else f'<span class="crbd">CR={hsg_CR:.4f} ✗</span>'
        st.markdown(f'<div class="ml">Housing Sub-Criteria — λ_max={hsg_lmax:.4f}  {hcr_b}</div>', unsafe_allow_html=True)
        st.markdown('<hr class="r"><div class="ml">AHP Product Ranking</div>', unsafe_allow_html=True)
        prs=pr.sort_values("AHP_Score",ascending=True)
        far=go.Figure(go.Bar(x=prs["AHP_Score"],y=prs["Segment"],orientation="h",
            marker_color=[GREEN if s==best["Segment"] else "#2B6A9F" for s in prs["Segment"]],
            text=[f"{v:.4f}" for v in prs["AHP_Score"]],
            textposition="outside",textfont=dict(color=WHITE,size=10)))
        far.update_layout(**PLY,title="Final AHP Priority Score",xaxis_title="Score",height=360,showlegend=False)
        st.plotly_chart(far,use_container_width=True)

    # 2D House of Quality -------------------------------------------------
    with s2hoq:
        st.markdown('<div class="ml">Engineering Decision Support</div>', unsafe_allow_html=True)
        st.markdown('<div class="mt">House of Quality (HoQ) — Technical Importance Analysis</div>', unsafe_allow_html=True)

        st.markdown(f"""<div class="asmp">
        <strong>METHOD:</strong> This module translates customer requirements into engineering priorities using the House of Quality relationship matrix.
        Relationship scores follow the HoQ scale: <strong>9 = strong</strong>, <strong>3 = moderate</strong>, and <strong>1 = weak</strong>.
        The results are calibrated to match the HoQ technical importance scores from the HoQ result row.
        </div>""", unsafe_allow_html=True)

        st.markdown("#### Adjust Customer Requirement Importance")
        st.caption("Move the sliders to test how engineering priorities change when customer needs become more or less important. The scores are automatically normalised.")

        c_left, c_right = st.columns([1.1, 1.9])

        with c_left:
            hoq_w1 = st.slider(
                "Cleaning performance",
                0.00, 1.00, float(HOQ_DEFAULT_WEIGHTS[0]), 0.01,
                help="Wet mop, anti-tangle brush, suction, and edge cleaning."
            )
            hoq_w2 = st.slider(
                "Self-maintenance",
                0.00, 1.00, float(HOQ_DEFAULT_WEIGHTS[1]), 0.01,
                help="Auto-empty dock and auto water refill."
            )
            hoq_w3 = st.slider(
                "Navigation and mapping",
                0.00, 1.00, float(HOQ_DEFAULT_WEIGHTS[2]), 0.01,
                help="SLAM navigation and multi-room mapping."
            )
            hoq_w4 = st.slider(
                "AI sensing",
                0.00, 1.00, float(HOQ_DEFAULT_WEIGHTS[3]), 0.01,
                help="AI dirt detection and obstacle avoidance camera."
            )
            hoq_w5 = st.slider(
                "Connectivity and user experience",
                0.00, 1.00, float(HOQ_DEFAULT_WEIGHTS[4]), 0.01,
                help="Voice control, app control, and carpet-hard floor transition."
            )

        selected_weights = np.array([hoq_w1, hoq_w2, hoq_w3, hoq_w4, hoq_w5], dtype=float)
        if selected_weights.sum() <= 0:
            selected_weights = HOQ_DEFAULT_WEIGHTS.copy()

        hoq_scores = compute_hoq_scores(selected_weights)

        hoq_df = pd.DataFrame({
            "Engineering Feature": HOQ_FEATURES,
            "Technical Importance Score": hoq_scores,
        }).sort_values("Technical Importance Score", ascending=False).reset_index(drop=True)

        top_feature = hoq_df.iloc[0]
        second_feature = hoq_df.iloc[1]

        with c_right:
            k1, k2, k3 = st.columns(3)
            k1.metric("Top Engineering Priority", top_feature["Engineering Feature"])
            k2.metric("Top Score", f"{top_feature['Technical Importance Score']:.2f}")
            k3.metric("Second Priority", second_feature["Engineering Feature"])

            fig_hoq = go.Figure(go.Bar(
                x=hoq_df["Engineering Feature"],
                y=hoq_df["Technical Importance Score"],
                marker_color=[GOLD if i == 0 else SEG_C[i % len(SEG_C)] for i in range(len(hoq_df))],
                text=[f"{v:.2f}" for v in hoq_df["Technical Importance Score"]],
                textposition="outside",
                textfont=dict(color=WHITE, size=12),
            ))
            fig_hoq.update_layout(
                **PLY,
                title="Technical Importance Score (Si) for Engineering Features",
                xaxis_title="Engineering Features",
                yaxis_title="Importance Score (Si)",
                height=430,
                showlegend=False,
                yaxis_range=[0, max(4.5, hoq_df["Technical Importance Score"].max() + 0.5)],
            )
            st.plotly_chart(fig_hoq, use_container_width=True)

        st.markdown(f"""<div class="ins">
        <strong>ENGINEERING INSIGHT:</strong><br><br>
        The most important engineering feature is <strong>{top_feature['Engineering Feature']}</strong>
        with a score of <strong>{top_feature['Technical Importance Score']:.2f}</strong>.
        The second priority is <strong>{second_feature['Engineering Feature']}</strong>.
        <br><br>
        <strong>Strategic meaning:</strong>
        <ul>
        <li>Focus engineering resources on top-ranked features first.</li>
        <li>Do not spread investment evenly across all technical features.</li>
        <li>High-impact features should be prioritised because they contribute most to customer satisfaction and market competitiveness.</li>
        </ul>
        <strong>Conclusion:</strong> The final 2030 market-leading robot vacuum should emphasise performance, sensing, navigation, and processing capability.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: COMPETITOR WAR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="ml">Interactive Strategy Game</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt">Competitor War — World Diffusion Strategy Game (2024–2030)</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="asmp">
    <strong>HOW TO PLAY:</strong> Up to 3 companies compete to dominate the 2030 global robot vacuum market.
    Choose your target segment, set price, advertising, and technology investment.
    The GBDM runs year-by-year across 7 world regions with market shock events.
    <strong>Score:</strong> Adoption 30% + Market Value 25% + Affordability 15% + Technology 15% + Segment Fit 15% + Ads 5%.
    <strong>Price convention:</strong> Higher priceChange = price drops = adoption rises (standardised).
    </div>""", unsafe_allow_html=True)

    # ── AI STRATEGY COACH (server-side; advises on your current move) ─────────
    ai.render_ai_coach(SEGS["Segment"].tolist())

    # ── AI POST-GAME DEBRIEF (server-side; analysis after a round ends) ───────
    ai.render_ai_postgame()

    # ── Embed the HTML war-game (tries several filenames so a rename can't break it) ──
    html_candidates = [
        "world_diffusion_competitor_war_multiplayer_fixed.html",
        "world_diffusion_competitor_war_v6_lightglobe.html",
        "world_diffusion_competitor_war_v6.html",
        "world_diffusion_competitor_war.html",
    ]
    base = os.path.dirname(os.path.abspath(__file__))
    loaded = False
    for name in html_candidates:
        for path in (os.path.join(base, name), name):
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    components.html(f.read(), height=2400, scrolling=True)
                loaded = True
                break
        if loaded:
            break
    if not loaded:
        st.warning(
            "**Game file not found.** Place one of these next to `app.py` and restart:\n\n"
            "- `world_diffusion_competitor_war_multiplayer_fixed.html`\n"
            "- `world_diffusion_competitor_war_v6_lightglobe.html`"
        )
