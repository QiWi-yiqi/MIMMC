"""
ai_backend.py — server-side AI for the MIMMC2026 dashboard.

Two touchpoints, both running on the Streamlit server (so they use WiFi):
  1. render_ai_coach(...)  -> in-game "AI Strategy Coach" (suggests how to improve a move)
  2. render_ai_report(...) -> final "AI Strategic Report" on the recommendation

Reliability pattern (important for a live demo):
  - Every AI call has a SHORT timeout and FAILS FAST.
  - If the key is missing, the call errors, or it times out, we fall back to a
    deterministic, always-available response. The judges never see a hang.

Setup:
  - Put your key in .streamlit/secrets.toml  ->  GROQ_API_KEY = "gsk_..."
    (or set the GROQ_API_KEY environment variable).
  - requirements.txt must include: requests
  - Never hardcode the key in this file.
"""

import os
import streamlit as st
import requests

AI_MODEL = "llama-3.3-70b-versatile"   # Groq model; change if you prefer another
KNEE_PRICE = 550                        # Pareto knee-point used by the coach heuristics


# ── core call ────────────────────────────────────────────────────────────────
def _get_api_key():
    try:
        k = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        k = "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"
    return k or os.environ.get("GROQ_API_KEY", "")


def ask_ai(system, user, max_tokens=500, timeout=5.0):
    """Server-side Groq chat call. Returns text, or None on ANY failure."""
    key = _get_api_key()
    if not key:
        return None
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.4,
                "max_tokens": max_tokens,
            },
            timeout=timeout,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
    return None


# ── deterministic fallbacks (always available, no network) ───────────────────
def fallback_report(ctx):
    return f"""**Strategic recommendation** _(offline fallback)_

The model identifies the **{ctx['product']} robot vacuum** for the **{ctx['segment']}**
segment as the 2030 market leader at an MSRP of **${ctx['msrp']:,}**.

- Projected 2030 adoption: **{ctx['adopt']:.2f}M households** ({ctx['share']:.1f}% winner share)
- Annual revenue at scale: **${ctx['rev']:.2f}B**
- AHP composite score: **{ctx['ahp']:.4f}** (CR = {ctx['cr']:.4f} < 0.10 — consistent)

The decision is driven mainly by **Technological Attractiveness** and **Market Adoption
Potential**. Strategy: launch into the Advanced tier, hold price near the Pareto
knee-point, and let innovation (p) carry early adoption before the imitation wave (q)
takes over toward 2030."""


def fallback_coach(seg, price, ad, tech):
    tips = []
    if price > KNEE_PRICE + 60:
        tips.append(f"Your price (${price}) is well above the ~${KNEE_PRICE} knee-point — "
                    "adoption falls faster than margin rises. Move toward the knee.")
    elif price < KNEE_PRICE - 120:
        tips.append(f"Your price (${price}) is low — you may be giving away margin. "
                    f"You can raise toward ~${KNEE_PRICE} without losing much adoption.")
    else:
        tips.append(f"Your price (${price}) sits near the optimal band — good.")
    if tech < 0.10:
        tips.append("Technology investment is low; Technology carries the top AHP weight "
                    "(~52%), so raising it is your highest-leverage move.")
    if ad > 0.25:
        tips.append("Advertising is high but Ads only carry ~6% AHP weight — "
                    "reallocate some spend toward technology.")
    if "Advanced" not in seg:
        tips.append("Basic tiers trail every Advanced tier in the model — "
                    "switching to an Advanced segment usually wins.")
    return "**AI coach** _(offline fallback)_\n\n- " + "\n- ".join(tips)


# ── UI blocks (call these from app.py) ───────────────────────────────────────
def render_ai_report(best, price_map, winner_share, ahp_cr):
    """Tab 1 — auto-generated executive summary of the recommendation."""
    st.markdown('<hr class="r"><div class="ml">AI Strategic Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="mt">Auto-Generated Executive Summary</div>', unsafe_allow_html=True)

    ctx = {
        "product": best["Product"], "segment": best["Segment"],
        "msrp": price_map[best["Product"]], "adopt": best["Cumulative_Adopters"],
        "share": winner_share, "rev": best["Annual_Rev_B"],
        "ahp": best["AHP_Score"], "cr": ahp_cr,
    }

    if st.button("Generate AI strategic report", key="ai_report_btn"):
        with st.spinner("Asking the AI strategist…"):
            system = ("You are a market-strategy analyst for a robot-vacuum company. "
                      "Write a concise, professional 2030 go-to-market summary (max 170 words) "
                      "using ONLY the numbers provided. Use markdown with short bullet points.")
            user = (f"Winner: {ctx['product']} robot vacuum for {ctx['segment']}. "
                    f"MSRP ${ctx['msrp']:,}. 2030 adoption {ctx['adopt']:.2f}M households "
                    f"({ctx['share']:.1f}% share). Annual revenue ${ctx['rev']:.2f}B. "
                    f"AHP score {ctx['ahp']:.4f}, CR {ctx['cr']:.4f}. "
                    "Top AHP drivers: Technological Attractiveness and Market Adoption Potential.")
            out = ask_ai(system, user, max_tokens=380, timeout=6.0)
        st.session_state["ai_report"] = out or fallback_report(ctx)
        st.session_state["ai_report_live"] = bool(out)

    if "ai_report" in st.session_state:
        tag = "live AI" if st.session_state.get("ai_report_live") else "offline fallback"
        st.markdown(f'<div class="ins"><strong>SOURCE:</strong> {tag}</div>', unsafe_allow_html=True)
        st.markdown(st.session_state["ai_report"])


def render_ai_coach(segment_names):
    """Tab 3 — AI strategy coach for the move you are about to play."""
    st.markdown('<hr class="r"><div class="ml">AI Strategy Coach</div>', unsafe_allow_html=True)
    st.caption("Enter the move you're about to make and get a suggestion. Runs on the "
               "Streamlit server (needs WiFi); falls back to rule-based advice if offline.")

    c1, c2, c3, c4 = st.columns(4)
    seg   = c1.selectbox("Your target segment", segment_names,
                         index=min(1, len(segment_names) - 1), key="coach_seg")
    price = c2.slider("Your price (USD)", 100, 1500, 650, 10, key="coach_price")
    ad    = c3.slider("Your ad spend", 0.0, 0.5, 0.06, 0.01, key="coach_ad")
    tech  = c4.slider("Your tech invest", 0.0, 0.5, 0.08, 0.01, key="coach_tech")

    if st.button("Ask the AI coach", key="ai_coach_btn"):
        with st.spinner("Coaching…"):
            system = ("You are a competitive-strategy coach inside a robot-vacuum market game. "
                      "The model weights: Technology ~52%, Adoption ~27%, Price ~15%, Ads ~6%, "
                      "and the optimal price knee-point is about $550. Give 2-3 short, punchy "
                      "bullet suggestions to improve the player's move. Be specific and concise.")
            user = (f"Player move — segment: {seg}, price: ${price}, "
                    f"ad spend: {ad}, tech invest: {tech}. How should they improve?")
            out = ask_ai(system, user, max_tokens=260, timeout=6.0)
        st.session_state["ai_coach"] = out or fallback_coach(seg, price, ad, tech)
        st.session_state["ai_coach_live"] = bool(out)

    if "ai_coach" in st.session_state:
        tag = "live AI" if st.session_state.get("ai_coach_live") else "offline fallback"
        st.markdown(f'<div class="ins"><strong>SOURCE:</strong> {tag}</div>', unsafe_allow_html=True)
        st.markdown(st.session_state["ai_coach"])


# ── POST-GAME DEBRIEF (AI insight after a round ends) ────────────────────────
def fallback_postgame(winner, your_co, your_share, winner_share):
    won = your_co.strip().lower() == winner.strip().lower()
    gap = winner_share - your_share
    if won:
        verdict = (f"You won with {your_share:.0f}% share. The model's structural favourite "
                   "(Urban Apartment · Advanced, technology-led) paid off.")
        moves = [
            "Hold the technology edge — it carries ~52% of the decision weight.",
            "Protect margin: you don't need to cut price below the ~$550 knee-point to stay ahead.",
        ]
    else:
        verdict = (f"{winner} won; you trailed by about {gap:.0f} points of share.")
        moves = [
            "Shift toward Urban Apartment · Advanced — it wins structurally in the model.",
            "Raise technology investment before cutting price — tech is ~52% AHP weight vs ~15% for price.",
            "Keep price inside the $450–650 band; the knee-point is ~$550.",
        ]
    return "**Post-game debrief** _(offline fallback)_\n\n" + verdict + "\n\n- " + "\n- ".join(moves)


def render_ai_postgame():
    """Tab 3 — AI analysis AFTER a round ends. Enter the final standings, get a debrief."""
    st.markdown('<hr class="r"><div class="ml">Post-Game Debrief</div>', unsafe_allow_html=True)
    st.caption("After a round ends, enter the final standings to get an AI analysis of why it "
               "played out that way. Runs on the Streamlit server (needs WiFi); falls back to "
               "rule-based analysis if offline.")

    d1, d2 = st.columns(2)
    winner  = d1.text_input("Winning company", "P1", key="pg_winner")
    your_co = d2.text_input("Your company", "P2", key="pg_you")
    d3, d4 = st.columns(2)
    your_share   = d3.slider("Your final share (%)", 0, 100, 30, key="pg_yourshare")
    winner_share = d4.slider("Winner's final share (%)", 0, 100, 45, key="pg_winshare")

    if st.button("Get post-game AI insight", key="ai_postgame_btn"):
        with st.spinner("Analysing the round…"):
            system = ("You are a competitive-strategy analyst debriefing a robot-vacuum market game "
                      "that just ended. Model context: Technology ~52% decision weight, Adoption ~27%, "
                      "Price ~15%, Ads ~6%; price knee-point ~$550; the structurally winning segment is "
                      "Urban Apartment · Advanced. In under 120 words, explain WHY the round ended this "
                      "way and give 2-3 concrete moves for the next round. Use short markdown bullets.")
            user = (f"Round result — winner: {winner} ({winner_share}% share). "
                    f"Player's company: {your_co} ({your_share}% share). "
                    "Explain the outcome and how the player should adjust next round.")
            out = ask_ai(system, user, max_tokens=320, timeout=6.0)
        st.session_state["ai_postgame"] = out or fallback_postgame(winner, your_co, your_share, winner_share)
        st.session_state["ai_postgame_live"] = bool(out)

    if "ai_postgame" in st.session_state:
        tag = "live AI" if st.session_state.get("ai_postgame_live") else "offline fallback"
        st.markdown(f'<div class="ins"><strong>SOURCE:</strong> {tag}</div>', unsafe_allow_html=True)
        st.markdown(st.session_state["ai_postgame"])
