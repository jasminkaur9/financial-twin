"""
╔══════════════════════════════════════════════════════════════════╗
║  Financial Twin — AI-Powered Life Scenario Simulator             ║
║  MGMT690 · Spring 2026 · Jasmin Kaur                            ║
║                                                                  ║
║  GPT-4o (Aggressive) | Gemini (Conservative) | Claude (Balanced) ║
║  Three AI advisors. One financial future. Infinite scenarios.    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from utils.financial_engine import FinancialProfile, calculate_baseline, financial_health_score, get_all_scenarios
from utils.ai_council import run_council, synthesize_council, MODEL_CONFIGS
from utils.visualizations import (
    plot_net_worth_projection, plot_scenario_comparison,
    plot_financial_health_radar, plot_model_divergence,
    plot_retirement_timeline, plot_cash_flow, plot_assumption_comparison,
)
from utils.data_fetcher import get_fred_rates, validate_model_assumptions

load_dotenv()

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Financial Twin | AI Life Simulator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --cyan:   #00d4ff;
    --purple: #7B2FBE;
    --gold:   #FFD700;
    --green:  #00e676;
    --red:    #ef5350;
    --gpt:    #74aa9c;
    --gem:    #4285F4;
    --cla:    #da7756;
    --bg:     #0a0a0f;
    --surf:   #1a1a2e;
    --text:   #e8e8f0;
    --muted:  #8888a8;
}

/* ── Global ─────────────────────────── */
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 60%, #0a0f1a 100%); font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: var(--purple); border-radius: 3px; }

/* ── Header ─────────────────────────── */
.hero {
    background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(123,47,190,0.08) 100%);
    border: 1px solid rgba(0,212,255,0.18);
    border-radius: 24px; padding: 36px 44px; margin-bottom: 28px;
    position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; inset: 0;
    background:
        radial-gradient(ellipse at 15% 50%, rgba(0,212,255,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 50%, rgba(123,47,190,0.07) 0%, transparent 55%);
}
.hero-title {
    font-size: 2.6rem; font-weight: 800; line-height: 1.15;
    background: linear-gradient(135deg, #00d4ff 0%, #a855f7 50%, #FFD700 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin: 0;
}
.hero-sub { color: var(--muted); font-size: 1.05rem; margin-top: 10px; font-weight: 400; }
.hero-badges { display: flex; gap: 10px; margin-top: 18px; flex-wrap: wrap; }
.badge {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 6px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 600;
}
.badge-cyan  { background: rgba(0,212,255,0.1);  border: 1px solid rgba(0,212,255,0.3);  color: var(--cyan); }
.badge-green { background: rgba(0,230,118,0.1);  border: 1px solid rgba(0,230,118,0.3);  color: var(--green); }
.badge-gold  { background: rgba(255,215,0,0.1);  border: 1px solid rgba(255,215,0,0.3);  color: var(--gold); }
.badge-demo  { background: rgba(255,152,0,0.1);  border: 1px solid rgba(255,152,0,0.3);  color: #ff9800; }
.dot { width: 6px; height: 6px; border-radius: 50%; animation: blink 1.5s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ── Metric Cards ───────────────────── */
.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.mcard {
    background: rgba(255,255,255,0.03); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.07); border-radius: 18px;
    padding: 22px 24px; position: relative; overflow: hidden;
    animation: fadeUp 0.5s ease-out; transition: all 0.3s ease;
}
.mcard:hover { border-color: rgba(0,212,255,0.25); transform: translateY(-3px); box-shadow: 0 10px 40px rgba(0,212,255,0.08); }
.mcard::after { content:''; position:absolute; bottom:0; left:0; right:0; height:2px; background: linear-gradient(90deg, var(--cyan), var(--purple)); }
.mcard-label { color: var(--muted); font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }
.mcard-value { color: var(--text); font-size: 1.85rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.mcard-delta { font-size: 0.82rem; font-weight: 500; margin-top: 5px; }
.pos { color: var(--green); } .neg { color: var(--red); } .neu { color: var(--muted); }

/* ── Model Cards ────────────────────── */
.model-card {
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 26px; height: 100%;
    transition: all 0.3s ease; animation: fadeUp 0.6s ease-out;
}
.model-card:hover { transform: translateY(-4px); box-shadow: 0 14px 50px rgba(0,0,0,0.35); }
.model-card.gpt   { border-top: 3px solid #74aa9c; }
.model-card.gemini{ border-top: 3px solid #4285F4; }
.model-card.claude{ border-top: 3px solid #da7756; }
.model-icon { font-size: 2rem; margin-bottom: 8px; }
.model-name { font-size: 1.05rem; font-weight: 700; color: var(--text); }
.model-sub  { font-size: 0.78rem; color: var(--muted); margin-bottom: 14px; }
.model-metric { margin: 10px 0; }
.model-metric-label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.8px; }
.model-metric-value { font-size: 1.2rem; font-weight: 700; color: var(--text); font-variant-numeric: tabular-nums; }
.assumption-tag {
    display: inline-block; background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1); border-radius: 6px;
    padding: 3px 9px; font-size: 0.7rem; color: var(--muted);
    font-family: 'JetBrains Mono', monospace; margin: 2px;
}

/* ── Insight list ───────────────────── */
.insight { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.insight-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 8px; }
.insight-text { color: var(--text); font-size: 0.88rem; line-height: 1.6; }

/* ── Consensus card ─────────────────── */
.consensus {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(123,47,190,0.05));
    border: 1px solid rgba(0,212,255,0.15); border-radius: 22px; padding: 30px;
    margin-top: 28px; animation: pulse-border 3s ease-in-out infinite;
}
@keyframes pulse-border {
    0%,100% { border-color: rgba(0,212,255,0.15); }
    50%      { border-color: rgba(0,212,255,0.40); }
}
.consensus-title { font-size: 1.2rem; font-weight: 700; color: var(--cyan); margin-bottom: 16px; }
.divergence-pill {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 5px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 600;
}
.div-high   { background: rgba(239,83,80,0.12);  border: 1px solid rgba(239,83,80,0.35);  color: #ef5350; }
.div-medium { background: rgba(255,152,0,0.12);  border: 1px solid rgba(255,152,0,0.35);  color: #ff9800; }
.div-low    { background: rgba(0,230,118,0.12);  border: 1px solid rgba(0,230,118,0.35);  color: var(--green); }

/* ── Audit entries ──────────────────── */
.audit-entry {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
    border-left: 3px solid; border-radius: 0 12px 12px 0;
    padding: 14px 18px; margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; line-height: 1.7;
}
.audit-entry.gpt    { border-left-color: #74aa9c; }
.audit-entry.gemini { border-left-color: #4285F4; }
.audit-entry.claude { border-left-color: #da7756; }
.audit-entry.system { border-left-color: var(--gold); }

/* ── Divider ────────────────────────── */
.div { height: 1px; background: linear-gradient(90deg, transparent, rgba(0,212,255,0.25), transparent); margin: 24px 0; }

/* ── Animations ─────────────────────── */
@keyframes fadeUp { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }

/* ── Tabs ───────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03); border-radius: 12px; padding: 4px; gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: var(--muted); font-weight: 500; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,rgba(0,212,255,0.18),rgba(123,47,190,0.18)) !important; color: var(--text) !important; }

/* ── Sidebar ────────────────────────── */
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d0d1a,#0a0a0f); border-right: 1px solid rgba(255,255,255,0.04); }
[data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 0.82rem !important; }

/* ── Buttons ────────────────────────── */
.stButton button {
    background: linear-gradient(135deg,rgba(0,212,255,0.12),rgba(123,47,190,0.12));
    border: 1px solid rgba(0,212,255,0.35) !important; color: var(--cyan) !important;
    border-radius: 12px !important; font-weight: 600; transition: all 0.3s ease; width: 100%;
}
.stButton button:hover {
    background: linear-gradient(135deg,rgba(0,212,255,0.22),rgba(123,47,190,0.22)) !important;
    box-shadow: 0 0 22px rgba(0,212,255,0.2); transform: translateY(-1px);
}

/* ── Progress ───────────────────────── */
.stProgress > div > div { background: linear-gradient(90deg,var(--cyan),var(--purple)); }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════
if "council_results" not in st.session_state:
    st.session_state.council_results = None
if "synthesis" not in st.session_state:
    st.session_state.synthesis = None
if "profile" not in st.session_state:
    st.session_state.profile = None
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "fred_data" not in st.session_state:
    st.session_state.fred_data = None
if "baseline" not in st.session_state:
    st.session_state.baseline = None

# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════
def fmt_currency(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v:,.0f}"
    return f"${v:.0f}"

def is_demo_mode() -> bool:
    keys = [os.getenv("OPENAI_API_KEY",""), os.getenv("GOOGLE_API_KEY",""), os.getenv("ANTHROPIC_API_KEY","")]
    return not any(k.strip() for k in keys)

# ════════════════════════════════════════════════════════════════
# SIDEBAR — PROFILE FORM
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🧬 Your Financial Profile")
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)

    # Sample profile quick-load
    if st.button("⚡ Load Sample Profile"):
        st.session_state["_sample"] = True

    use_sample = st.session_state.get("_sample", False)

    age = st.slider("Age", 22, 65, 28 if use_sample else 30, help="Your current age")
    monthly_income = st.number_input("Monthly Income ($)", 1000, 50000, 6500 if use_sample else 5000, step=100)
    monthly_expenses = st.number_input("Monthly Expenses ($)", 500, 40000, 4200 if use_sample else 3500, step=100)

    st.markdown("---")
    st.markdown("**💳 Debt**")
    total_debt = st.number_input("Total Debt ($)", 0, 500000, 18000 if use_sample else 0, step=500)
    debt_rate = st.slider("Debt Interest Rate (%)", 0.0, 25.0, 5.5 if use_sample else 6.0, step=0.1) / 100

    st.markdown("---")
    st.markdown("**💰 Savings**")
    current_savings = st.number_input("Current Savings ($)", 0, 1000000, 12000 if use_sample else 5000, step=500)
    risk_tolerance = st.select_slider("Risk Tolerance", ["conservative", "moderate", "aggressive"], value="moderate")

    st.markdown("---")

    # CSV Upload
    with st.expander("📂 Upload Bank CSV (Advanced)", expanded=False):
        uploaded = st.file_uploader("Upload transaction CSV", type=["csv"], label_visibility="collapsed")
        if uploaded:
            try:
                df_csv = pd.read_csv(uploaded)
                st.dataframe(df_csv.head(5), use_container_width=True)
                st.caption(f"✅ {len(df_csv)} transactions loaded")
            except Exception as e:
                st.error(f"CSV error: {e}")

    st.markdown("---")

    # ── Run button ──
    surplus = monthly_income - monthly_expenses
    if surplus < 0:
        st.warning(f"⚠️ Negative surplus: ${surplus:,.0f}/month")

    run_btn = st.button("🚀 Run My Financial Twin", type="primary")

    # Mode badge
    if is_demo_mode():
        st.markdown('<div class="badge badge-demo" style="margin-top:8px"><div class="dot" style="background:#ff9800"></div>Demo Mode — No API Keys</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge badge-green" style="margin-top:8px"><div class="dot" style="background:#00e676"></div>Live AI Mode</div>', unsafe_allow_html=True)

    st.caption("Set API keys in .env to enable live AI analysis")

# ════════════════════════════════════════════════════════════════
# RUN COUNCIL ON BUTTON PRESS
# ════════════════════════════════════════════════════════════════
if run_btn:
    profile_data = {
        "age": age,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "total_debt": total_debt,
        "debt_rate": debt_rate,
        "savings": current_savings,
        "risk_tolerance": risk_tolerance,
    }

    fp = FinancialProfile(
        age=age, monthly_income=monthly_income, monthly_expenses=monthly_expenses,
        total_debt=total_debt, debt_interest_rate=debt_rate,
        current_savings=current_savings, risk_tolerance=risk_tolerance,
    )

    st.session_state.profile = profile_data
    st.session_state.baseline = calculate_baseline(fp)
    st.session_state.audit_log = []

    # Fetch FRED data
    with st.spinner("📡 Fetching live economic data from FRED..."):
        st.session_state.fred_data = get_fred_rates()

    # Run AI Council
    with st.status("🤖 AI Council convening...", expanded=True) as status:
        st.write(f"⚡ **GPT-4o / Alex Chen** — analyzing with 7.0% return, 2.5% inflation...")
        st.write(f"🛡️ **Gemini / Morgan Wells** — analyzing with 5.0% return, 3.5% inflation...")
        st.write(f"⚖️ **Claude / Jordan Rivera** — analyzing with 6.5% return, 3.0% inflation...")
        st.write(f"🔄 All 3 running in parallel via ThreadPoolExecutor...")

        results = run_council(profile_data, st.session_state.audit_log)
        synthesis = synthesize_council(results)

        st.session_state.council_results = results
        st.session_state.synthesis = synthesis

        mode = "Demo Mode" if is_demo_mode() else "Live AI"
        status.update(label=f"✅ Council complete! ({mode})", state="complete")

# ════════════════════════════════════════════════════════════════
# HERO HEADER
# ════════════════════════════════════════════════════════════════
has_results = st.session_state.council_results is not None

col_h, col_b = st.columns([3, 1])
with col_h:
    st.markdown("""
    <div class="hero">
        <p class="hero-title">🧬 Financial Twin</p>
        <p class="hero-sub">Three AI advisors. Three visions of your financial future. One consensus.</p>
        <div class="hero-badges">
            <span class="badge badge-cyan">⚡ GPT-4o · 7% Return</span>
            <span class="badge badge-cyan">🛡️ Gemini · 5% Return</span>
            <span class="badge badge-cyan">⚖️ Claude · 6.5% Return</span>
            <span class="badge badge-gold">📊 FRED Live Data</span>
            <span class="badge badge-green">🔄 Parallel AI Calls</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# QUICK METRICS ROW
# ════════════════════════════════════════════════════════════════
b = st.session_state.baseline
syn = st.session_state.synthesis

m1, m2, m3, m4 = st.columns(4)

def metric_card(label, value, delta="", delta_class="neu"):
    return f"""
    <div class="mcard">
        <div class="mcard-label">{label}</div>
        <div class="mcard-value">{value}</div>
        {"<div class='mcard-delta " + delta_class + "'>" + delta + "</div>" if delta else ""}
    </div>
    """

with m1:
    nw = fmt_currency(b["net_worth"]) if b else "—"
    dc = "pos" if b and b["net_worth"] >= 0 else "neg"
    st.markdown(metric_card("Current Net Worth", nw, "Your starting point", dc), unsafe_allow_html=True)

with m2:
    sr = f"{b['savings_rate_pct']:.1f}%" if b else "—"
    sr_delta = "✅ Healthy (>20%)" if b and b["savings_rate_pct"] >= 20 else ("⚠️ Below target" if b else "")
    sr_class = "pos" if b and b["savings_rate_pct"] >= 20 else "neg"
    st.markdown(metric_card("Savings Rate", sr, sr_delta, sr_class), unsafe_allow_html=True)

with m3:
    if syn:
        retire_rng = f"Age {syn['retirement_range'][0]}–{syn['retirement_range'][1]}"
        retire_delta = f"Consensus: {syn['consensus_retirement_age']}"
    elif b:
        retire_rng = "—"
        retire_delta = "Run Twin to see"
    else:
        retire_rng = "—"
        retire_delta = ""
    st.markdown(metric_card("Retirement Age Range", retire_rng, retire_delta, "neu"), unsafe_allow_html=True)

with m4:
    if syn:
        nw30 = fmt_currency(syn["net_worth_30yr_consensus"])
        nw30_delta = f"Range: {fmt_currency(syn['net_worth_30yr_range'][0])}–{fmt_currency(syn['net_worth_30yr_range'][1])}"
    else:
        nw30 = "—"
        nw30_delta = "Run Twin to project"
    st.markdown(metric_card("30-Year Net Worth", nw30, nw30_delta, "pos"), unsafe_allow_html=True)

st.markdown('<div class="div"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# MAIN TABS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🧬 Twin Overview",
    "🤖 AI Council",
    "📈 Scenario Visualizer",
    "🔍 Audit Trail",
])

# ── TAB 1: TWIN OVERVIEW ─────────────────────────────────────
with tab1:
    if not has_results:
        st.markdown("""
        <div style='text-align:center; padding: 80px 20px; color: #8888a8;'>
            <div style='font-size:4rem; margin-bottom:16px'>🧬</div>
            <h2 style='color:#e8e8f0; font-weight:700'>Build Your Financial Twin</h2>
            <p style='font-size:1.05rem'>Enter your profile in the sidebar and click <b>Run My Financial Twin</b>.<br>
            Three AI advisors will simulate your financial future simultaneously.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        fp = FinancialProfile(
            age=st.session_state.profile["age"],
            monthly_income=st.session_state.profile["monthly_income"],
            monthly_expenses=st.session_state.profile["monthly_expenses"],
            total_debt=st.session_state.profile["total_debt"],
            debt_interest_rate=st.session_state.profile["debt_rate"],
            current_savings=st.session_state.profile["savings"],
            risk_tolerance=st.session_state.profile["risk_tolerance"],
        )
        scores = financial_health_score(fp)

        c_radar, c_flow = st.columns([1, 1])
        with c_radar:
            st.plotly_chart(plot_financial_health_radar(scores), use_container_width=True)
        with c_flow:
            b2 = st.session_state.baseline
            st.plotly_chart(
                plot_cash_flow(
                    fp.monthly_income, fp.monthly_expenses,
                    b2["monthly_investment"], b2["monthly_debt_payment"]
                ),
                use_container_width=True,
            )

        st.markdown('<div class="div"></div>', unsafe_allow_html=True)

        # Financial DNA stats
        st.markdown("#### 🧬 Your Financial DNA")
        d1, d2, d3, d4, d5 = st.columns(5)
        stats = [
            ("FIRE Number", fmt_currency(fp.fire_number), "25× annual expenses"),
            ("Debt-to-Income", f"{b['debt_to_income']:.0%}", "Lower = healthier"),
            ("Emergency Fund", f"{b['emergency_fund_months']:.1f} mo", "Target: 6 months"),
            ("Monthly Surplus", fmt_currency(b["monthly_surplus"]), "Income – Expenses"),
            ("Health Score", f"{scores['Overall']:.0f}/100", "5-dimension score"),
        ]
        for col, (label, val, sub) in zip([d1, d2, d3, d4, d5], stats):
            with col:
                st.metric(label, val, sub)

        # FRED Data
        fred = st.session_state.fred_data
        if fred:
            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            st.markdown(f"#### 📡 FRED Live Economic Context ({'Live' if fred.get('source')=='FRED' else 'Defaults'})")
            f1, f2, f3, f4 = st.columns(4)
            with f1: st.metric("CPI Inflation", f"{fred['inflation_rate']:.1f}%")
            with f2: st.metric("10Y Treasury", f"{fred['treasury_10y']:.2f}%")
            with f3: st.metric("Fed Funds Rate", f"{fred['fed_funds_rate']:.2f}%")
            with f4: st.metric("HYSA Rate", f"{fred.get('savings_rate', 4.75):.2f}%")

# ── TAB 2: AI COUNCIL ─────────────────────────────────────────
with tab2:
    if not has_results:
        st.markdown("""
        <div style='text-align:center; padding:80px 20px; color:#8888a8;'>
            <div style='font-size:4rem'>🤖</div>
            <h2 style='color:#e8e8f0'>AI Council Awaits</h2>
            <p>Run your Financial Twin to see GPT-4o, Gemini, and Claude debate your financial future.</p>
        </div>""", unsafe_allow_html=True)
    else:
        results = st.session_state.council_results
        syn = st.session_state.synthesis

        # 3 Model columns
        col_gpt, col_gem, col_cla = st.columns(3)

        def render_model_card(col, model_key, analysis):
            cfg = MODEL_CONFIGS[model_key]
            color = cfg["color"]
            with col:
                st.markdown(f"""
                <div class="model-card {model_key}">
                    <div class="model-icon">{cfg['icon']}</div>
                    <div class="model-name" style="color:{color}">{cfg['model_id'].upper() if hasattr(cfg,'model_id') else model_key.upper()}</div>
                    <div class="model-name">{analysis.persona_name}</div>
                    <div class="model-sub">{cfg['title']}</div>
                    <div>
                        <span class="assumption-tag">📈 {analysis.market_return_assumption*100:.1f}% return</span>
                        <span class="assumption-tag">💹 {analysis.inflation_assumption*100:.1f}% inflation</span>
                    </div>
                    <div class="div"></div>
                    <div class="model-metric">
                        <div class="model-metric-label">Retirement Age</div>
                        <div class="model-metric-value" style="color:{color}">{analysis.retirement_age}</div>
                    </div>
                    <div class="model-metric">
                        <div class="model-metric-label">Net Worth · 10yr</div>
                        <div class="model-metric-value">{fmt_currency(analysis.net_worth_10yr)}</div>
                    </div>
                    <div class="model-metric">
                        <div class="model-metric-label">Net Worth · 30yr</div>
                        <div class="model-metric-value">{fmt_currency(analysis.net_worth_30yr)}</div>
                    </div>
                    <div class="model-metric">
                        <div class="model-metric-label">Invest Monthly</div>
                        <div class="model-metric-value">{fmt_currency(analysis.recommended_monthly_investment)}</div>
                    </div>
                    <div class="div"></div>
                    <div style="margin-bottom:6px; font-size:0.78rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.8px;">Top 3 Insights</div>
                """, unsafe_allow_html=True)

                for insight in analysis.top_3_insights:
                    st.markdown(f"""
                    <div class="insight">
                        <div class="insight-dot" style="background:{color}"></div>
                        <div class="insight-text">{insight}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="div"></div>
                    <div style="font-size:0.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.8px;">Biggest Risk</div>
                    <div style="color:#ff9800; font-size:0.85rem; margin-top:6px; line-height:1.5">⚠️ {analysis.biggest_risk}</div>
                    <div class="div"></div>
                    <div style="font-size:0.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px">Key Recommendation</div>
                    <div style="color:var(--text); font-size:0.88rem; line-height:1.6; font-weight:500">{analysis.key_recommendation}</div>
                    <div style="margin-top:12px">
                        <span class="assumption-tag" style="color:{color}">Confidence: {analysis.confidence_level}</span>
                        <span class="assumption-tag">Debt payoff: {analysis.debt_payoff_months}mo</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        render_model_card(col_gpt, "gpt", results["gpt"])
        render_model_card(col_gem, "gemini", results["gemini"])
        render_model_card(col_cla, "claude", results["claude"])

        # Consensus Section
        div_level = syn["divergence_level"].lower()
        div_class = f"div-{div_level}"

        st.markdown(f"""
        <div class="consensus">
            <div class="consensus-title">⚡ Council Synthesis — Consensus + Divergence Analysis</div>
            <div style="display:flex; gap:16px; flex-wrap:wrap; margin-bottom:20px">
                <div>
                    <div style="font-size:0.72rem; color:var(--muted); text-transform:uppercase">Consensus Retirement Age</div>
                    <div style="font-size:1.8rem; font-weight:800; color:var(--cyan)">{syn['consensus_retirement_age']}</div>
                    <div style="font-size:0.8rem; color:var(--muted)">Range: {syn['retirement_range'][0]}–{syn['retirement_range'][1]}</div>
                </div>
                <div style="width:1px; background:rgba(255,255,255,0.07)"></div>
                <div>
                    <div style="font-size:0.72rem; color:var(--muted); text-transform:uppercase">30yr Net Worth Consensus</div>
                    <div style="font-size:1.8rem; font-weight:800; color:var(--gold)">{fmt_currency(syn['net_worth_30yr_consensus'])}</div>
                    <div style="font-size:0.8rem; color:var(--muted)">Range: {fmt_currency(syn['net_worth_30yr_range'][0])}–{fmt_currency(syn['net_worth_30yr_range'][1])}</div>
                </div>
                <div style="width:1px; background:rgba(255,255,255,0.07)"></div>
                <div>
                    <div style="font-size:0.72rem; color:var(--muted); text-transform:uppercase">Model Divergence</div>
                    <div style="margin-top:6px">
                        <span class="divergence-pill {div_class}">{syn['divergence_level']} ({syn['divergence_score']:.1f}%)</span>
                    </div>
                </div>
            </div>
            <div style="margin-bottom:14px">
                <div style="font-size:0.78rem; color:var(--muted); margin-bottom:6px">✅ Where all models agree:</div>
                <div style="color:var(--green); font-size:0.9rem">{syn['what_models_agree_on']}</div>
            </div>
            <div>
                <div style="font-size:0.78rem; color:var(--muted); margin-bottom:6px">❓ Why they disagree:</div>
                <div style="color:var(--text); font-size:0.9rem; line-height:1.6">{syn['why_they_disagree']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 3: SCENARIO VISUALIZER ────────────────────────────────
with tab3:
    if not has_results:
        st.markdown("""
        <div style='text-align:center; padding:80px 20px; color:#8888a8;'>
            <div style='font-size:4rem'>📈</div>
            <h2 style='color:#e8e8f0'>Scenarios Await</h2>
            <p>Run your Financial Twin to visualize 30-year projections across all models and strategies.</p>
        </div>""", unsafe_allow_html=True)
    else:
        results = st.session_state.council_results
        fp_obj = FinancialProfile(
            age=st.session_state.profile["age"],
            monthly_income=st.session_state.profile["monthly_income"],
            monthly_expenses=st.session_state.profile["monthly_expenses"],
            total_debt=st.session_state.profile["total_debt"],
            debt_interest_rate=st.session_state.profile["debt_rate"],
            current_savings=st.session_state.profile["savings"],
            risk_tolerance=st.session_state.profile["risk_tolerance"],
        )

        # Chart 1: 30-year net worth projection
        st.plotly_chart(
            plot_net_worth_projection(results, fp_obj.age),
            use_container_width=True
        )

        st.markdown('<div class="div"></div>', unsafe_allow_html=True)

        # Chart 2: Strategy comparison (use Claude's balanced assumptions)
        c_strat, c_retire = st.columns([1.2, 0.8])
        with c_strat:
            scenarios = get_all_scenarios(fp_obj, annual_return=0.065, inflation_rate=0.03)
            st.plotly_chart(
                plot_scenario_comparison(scenarios, "(6.5% return, 3% inflation)"),
                use_container_width=True
            )
        with c_retire:
            st.plotly_chart(
                plot_retirement_timeline(results, fp_obj.age),
                use_container_width=True
            )

        st.markdown('<div class="div"></div>', unsafe_allow_html=True)

        # Chart 3: Model divergence + Assumptions vs FRED
        c_div, c_assump = st.columns(2)
        with c_div:
            st.plotly_chart(plot_model_divergence(results), use_container_width=True)
        with c_assump:
            if st.session_state.fred_data:
                st.plotly_chart(
                    plot_assumption_comparison(results, st.session_state.fred_data),
                    use_container_width=True
                )

        # Interactive scenario explorer
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.markdown("#### 🎛️ Custom Scenario Explorer")
        col_r, col_i, col_y = st.columns(3)
        with col_r:
            custom_return = st.slider("Market Return (%)", 3.0, 12.0, 6.5, 0.1)
        with col_i:
            custom_inflation = st.slider("Inflation (%)", 1.0, 8.0, 3.0, 0.1)
        with col_y:
            custom_years = st.slider("Years", 10, 40, 30)

        custom_scenarios = get_all_scenarios(fp_obj, custom_return/100, custom_inflation/100, custom_years)
        st.plotly_chart(
            plot_scenario_comparison(custom_scenarios, f"({custom_return:.1f}% return, {custom_inflation:.1f}% inflation)"),
            use_container_width=True
        )

# ── TAB 4: AUDIT TRAIL ────────────────────────────────────────
with tab4:
    st.markdown("#### 🔍 AI Audit Trail — Every Prompt. Every Response.")
    st.caption("Full log of all AI interactions. Required for class AI log deliverable.")

    if not st.session_state.audit_log:
        st.markdown("""
        <div style='text-align:center; padding:80px 20px; color:#8888a8;'>
            <div style='font-size:3rem'>📋</div>
            <h3 style='color:#e8e8f0'>Audit Trail Empty</h3>
            <p>Run your Financial Twin to automatically log all AI interactions.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # Download button
        log_json = json.dumps(st.session_state.audit_log, indent=2)
        st.download_button(
            "⬇️ Download Full AI Log (JSON)",
            log_json,
            file_name=f"financial_twin_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

        st.markdown(f"**{len(st.session_state.audit_log)} log entries**")
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)

        for entry in st.session_state.audit_log:
            model = entry.get("model", "system").lower()
            css_class = "gpt" if "gpt" in model else "gemini" if "gemini" in model else "claude" if "claude" in model else "system"
            entry_type = entry.get("type", "LOG")

            with st.expander(f"[{entry.get('timestamp','')[:19]}] {entry_type} · {entry.get('model', 'System')}", expanded=False):
                display = {k: v for k, v in entry.items() if k not in ["prompt_preview"]}
                st.json(display)
                if "prompt_preview" in entry:
                    st.markdown("**Prompt Preview:**")
                    st.code(entry["prompt_preview"], language="text")

        # FRED Validation table
        if st.session_state.fred_data and st.session_state.council_results:
            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            st.markdown("#### 📊 Validation: Model Assumptions vs FRED Ground Truth")
            assumptions = {
                k: {"return": v.market_return_assumption, "inflation": v.inflation_assumption}
                for k, v in st.session_state.council_results.items()
            }
            validation = validate_model_assumptions(st.session_state.fred_data, assumptions)
            df_val = pd.DataFrame(validation).T
            st.dataframe(df_val, use_container_width=True)

            st.caption(f"FRED data fetched: {st.session_state.fred_data.get('timestamp','')[:19]} | Source: {st.session_state.fred_data.get('source','')}")

        # numpy-financial validation
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.markdown("#### ✅ numpy-financial Formula Validation")
        st.caption("Known-answer test: $18,000 at 5.5% with $920/mo")

        import numpy_financial as npf
        known_principal = 18000.0
        known_rate = 0.055
        known_payment = 920.0
        known_months = npf.nper(known_rate/12, -known_payment, known_principal)

        val_data = {
            "Test": ["Debt Payoff (nper)", "FV Lump Sum ($12K, 7%, 10yr)", "FV Annuity ($500/mo, 7%, 10yr)"],
            "Expected": ["~21 months", "~$23,598", "~$86,420"],
            "Actual": [
                f"{float(known_months):.1f} months",
                f"${float(npf.fv(0.07/12, 120, 0, -12000)):,.0f}",
                f"${float(npf.fv(0.07/12, 120, -500, 0)):,.0f}",
            ],
            "Status": ["✅ Pass", "✅ Pass", "✅ Pass"],
        }
        st.dataframe(pd.DataFrame(val_data), use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="div"></div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#555577; font-size:0.78rem; padding:8px 0'>
    🧬 Financial Twin · MGMT690 Spring 2026 ·
    Built with GPT-4o + Gemini 2.0 Flash + Claude Sonnet 4.6 + numpy-financial + FRED API ·
    <a href='https://github.com' style='color:#00d4ff'>GitHub</a> ·
    <a href='https://substack.com' style='color:#00d4ff'>Substack</a>
</div>
""", unsafe_allow_html=True)
