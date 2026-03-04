"""
╔══════════════════════════════════════════════════════════╗
║  Financial Twin — AI-Powered Life Scenario Simulator     ║
║  MGMT690 · Spring 2026 · Jasmin Kaur                    ║
║  GPT-4o · Gemini 2.0 Flash · Claude Sonnet 4.6          ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import json, os
from datetime import datetime
from dotenv import load_dotenv

from utils.financial_engine import (
    FinancialProfile, calculate_baseline, financial_health_score,
    project_net_worth, get_all_scenarios, estimate_retirement_age
)
from utils.ai_council import run_council, synthesize_council, MODEL_CONFIGS
from utils.visualizations import (
    plot_net_worth_projection, plot_scenario_comparison,
    plot_financial_health_radar, plot_model_divergence,
    plot_retirement_timeline, plot_cash_flow, plot_assumption_comparison,
)
from utils.data_fetcher import get_fred_rates, validate_model_assumptions

load_dotenv()

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Twin | AI Life Simulator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

.stApp { background: linear-gradient(135deg,#0a0a0f 0%,#0d0d1a 60%,#0a0f1a 100%); font-family:'Inter',sans-serif; }
#MainMenu,footer,header{visibility:hidden}
.stDeployButton{display:none}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#0a0a0f}
::-webkit-scrollbar-thumb{background:#7B2FBE;border-radius:3px}

.hero{background:linear-gradient(135deg,rgba(0,212,255,.08),rgba(123,47,190,.08));border:1px solid rgba(0,212,255,.2);border-radius:24px;padding:32px 40px;margin-bottom:24px;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 15% 50%,rgba(0,212,255,.07) 0%,transparent 55%),radial-gradient(ellipse at 85% 50%,rgba(123,47,190,.07) 0%,transparent 55%)}
.hero-title{font-size:2.4rem;font-weight:800;background:linear-gradient(135deg,#00d4ff,#a855f7,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0}
.hero-sub{color:#8888a8;font-size:1rem;margin-top:8px}
.hero-tags{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.tag{padding:5px 12px;border-radius:20px;font-size:.75rem;font-weight:600;border:1px solid rgba(0,212,255,.3);color:#00d4ff;background:rgba(0,212,255,.08)}

.model-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:22px;transition:all .3s ease}
.model-card:hover{transform:translateY(-3px);box-shadow:0 12px 40px rgba(0,0,0,.3)}
.model-card.gpt{border-top:3px solid #74aa9c}
.model-card.gemini{border-top:3px solid #4285F4}
.model-card.claude{border-top:3px solid #da7756}

.consensus-box{background:linear-gradient(135deg,rgba(0,212,255,.05),rgba(123,47,190,.05));border:1px solid rgba(0,212,255,.2);border-radius:20px;padding:28px;margin-top:20px}

.insight-item{padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:.88rem;color:#e8e8f0;line-height:1.6}

.audit-block{background:rgba(255,255,255,.02);border-left:3px solid #00d4ff;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:8px;font-family:'JetBrains Mono',monospace;font-size:.78rem}

.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.03);border-radius:12px;padding:4px;gap:4px;border:1px solid rgba(255,255,255,.06)}
.stTabs [data-baseweb="tab"]{border-radius:8px;color:#8888a8;font-weight:500}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(0,212,255,.18),rgba(123,47,190,.18)) !important;color:#e8e8f0 !important}

[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d0d1a,#0a0a0f);border-right:1px solid rgba(255,255,255,.04)}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#8888a8;font-size:.82rem}

div[data-testid="stMetric"]{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:16px 20px;border-bottom:2px solid #00d4ff}
div[data-testid="stMetric"] label{color:#8888a8 !important;font-size:.72rem !important;text-transform:uppercase;letter-spacing:1px}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#e8e8f0;font-size:1.6rem;font-weight:700}

.stProgress > div > div{background:linear-gradient(90deg,#00d4ff,#7B2FBE)}

div[data-testid="stButton"] button{background:linear-gradient(135deg,rgba(0,212,255,.12),rgba(123,47,190,.12));border:1px solid rgba(0,212,255,.4) !important;color:#00d4ff !important;border-radius:12px !important;font-weight:600;transition:all .3s}
div[data-testid="stButton"] button:hover{background:linear-gradient(135deg,rgba(0,212,255,.22),rgba(123,47,190,.22)) !important;box-shadow:0 0 20px rgba(0,212,255,.2)}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────
DEFAULTS = {
    "council_results": None, "synthesis": None, "profile": None,
    "audit_log": [], "fred_data": None, "baseline": None, "health_scores": None,
    # Form field defaults
    "f_age": 30, "f_income": 5000, "f_expenses": 3500,
    "f_debt": 0, "f_debt_rate": 6.0, "f_savings": 5000, "f_risk": "moderate",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────
def fmt(v):
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:     return f"${v:,.0f}"
    return f"${v:.0f}"

def is_demo():
    return not any(os.getenv(k,"").strip() for k in ["OPENAI_API_KEY","GOOGLE_API_KEY","ANTHROPIC_API_KEY"])

def make_fp():
    return FinancialProfile(
        age=st.session_state.f_age,
        monthly_income=st.session_state.f_income,
        monthly_expenses=st.session_state.f_expenses,
        total_debt=st.session_state.f_debt,
        debt_interest_rate=st.session_state.f_debt_rate / 100,
        current_savings=st.session_state.f_savings,
        risk_tolerance=st.session_state.f_risk,
    )

def _profile_dict(fp):
    return {
        "age": fp.age, "monthly_income": fp.monthly_income,
        "monthly_expenses": fp.monthly_expenses, "total_debt": fp.total_debt,
        "debt_rate": fp.debt_interest_rate, "savings": fp.current_savings,
        "risk_tolerance": fp.risk_tolerance,
    }

# ── Auto-load: populate with demo data on first open ──────────
if st.session_state.council_results is None:
    from utils.ai_council import _generate_demo
    _fp0 = make_fp()
    _pd0 = _profile_dict(_fp0)
    _dr  = _generate_demo(_pd0)
    st.session_state.council_results = _dr
    st.session_state.synthesis       = synthesize_council(_dr)
    st.session_state.baseline        = calculate_baseline(_fp0)
    st.session_state.health_scores   = financial_health_score(_fp0)
    st.session_state.profile         = _pd0
    st.session_state.fred_data       = {
        "inflation_rate": 3.1, "treasury_10y": 4.5,
        "fed_funds_rate": 5.25, "savings_rate": 4.75, "source": "defaults",
    }
    st.session_state.audit_log       = []

# ── HERO ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">🧬 Financial Twin</p>
  <p class="hero-sub">Three AI advisors. Three visions of your financial future. One consensus.</p>
  <div class="hero-tags">
    <span class="tag">⚡ GPT-4o · 7% Return</span>
    <span class="tag">🛡️ Gemini · 5% Return</span>
    <span class="tag">⚖️ Claude · 6.5% Return</span>
    <span class="tag">📊 FRED Live Data</span>
    <span class="tag">🔄 Parallel AI Calls</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── PROFILE FORM (main area) ───────────────────────────────────
hdr_col, mode_col = st.columns([3, 1])
with hdr_col:
    st.markdown("### 🧬 Your Financial Profile")
with mode_col:
    mode_color = "#ff9800" if is_demo() else "#00e676"
    mode_label = "⚙️ Demo Mode" if is_demo() else "🟢 Live AI Mode"
    st.markdown(
        f'<div style="text-align:right;margin-top:12px;color:{mode_color};'
        f'font-size:.82rem;font-weight:600">{mode_label}</div>',
        unsafe_allow_html=True,
    )

if st.button("⚡ Load Sample Profile", help="Age 28 · $6,500 income · $18,000 debt at 5.5%"):
    st.session_state.f_age       = 28
    st.session_state.f_income    = 6500
    st.session_state.f_expenses  = 4200
    st.session_state.f_debt      = 18000
    st.session_state.f_debt_rate = 5.5
    st.session_state.f_savings   = 12000
    st.session_state.f_risk      = "moderate"
    st.rerun()

r1c1, r1c2, r1c3, r1c4 = st.columns(4)
with r1c1:
    st.slider("Age", 22, 65, int(st.session_state.f_age), key="f_age")
with r1c2:
    st.number_input("Monthly Income ($)", 1000, 100000, int(st.session_state.f_income), step=100, key="f_income")
with r1c3:
    st.number_input("Monthly Expenses ($)", 500, 80000, int(st.session_state.f_expenses), step=100, key="f_expenses")
with r1c4:
    st.number_input("Current Savings ($)", 0, 2000000, int(st.session_state.f_savings), step=500, key="f_savings")

r2c1, r2c2, r2c3, r2c4 = st.columns(4)
with r2c1:
    st.number_input("Total Debt ($)", 0, 500000, int(st.session_state.f_debt), step=500, key="f_debt")
with r2c2:
    st.slider("Debt Rate (%)", 0.0, 25.0, float(st.session_state.f_debt_rate), 0.1, key="f_debt_rate")
with r2c3:
    st.select_slider("Risk Tolerance", ["conservative", "moderate", "aggressive"],
                     value=st.session_state.f_risk, key="f_risk")
with r2c4:
    surplus = st.session_state.f_income - st.session_state.f_expenses
    if surplus <= 0:
        st.warning(f"⚠️ Deficit: ${surplus:,.0f}/mo")
    else:
        st.metric("Monthly Surplus", fmt(surplus))
    run_btn = st.button("🚀 Run My Financial Twin", type="primary", use_container_width=True)

st.divider()

# ── RUN COUNCIL ───────────────────────────────────────────────
if run_btn:
    try:
        fp = make_fp()
        profile_data = _profile_dict(fp)

        st.session_state.profile       = profile_data
        st.session_state.baseline      = calculate_baseline(fp)
        st.session_state.health_scores = financial_health_score(fp)
        st.session_state.audit_log     = []

        with st.spinner("🤖 AI Council running — GPT-4o · Gemini · Claude in parallel..."):
            st.session_state.fred_data    = get_fred_rates()
            results                       = run_council(profile_data, st.session_state.audit_log)
            synthesis                     = synthesize_council(results)
            st.session_state.council_results = results
            st.session_state.synthesis       = synthesis

        st.rerun()
    except Exception as _e:
        import traceback
        st.error(f"⚠️ Analysis error: {_e}")
        st.code(traceback.format_exc())

# ── METRIC ROW ────────────────────────────────────────────────
# Always recompute baseline from current form values so metrics update live
_fp_live = make_fp()
b   = calculate_baseline(_fp_live)
syn = st.session_state.synthesis

m1, m2, m3, m4 = st.columns(4)

with m1:
    delta = "✅ Positive" if b["net_worth"] >= 0 else "⚠️ Negative"
    st.metric("Current Net Worth", fmt(b["net_worth"]), delta)

with m2:
    delta = "✅ Healthy" if b["savings_rate_pct"] >= 20 else "⚠️ Below 20% target"
    st.metric("Savings Rate", f"{b['savings_rate_pct']:.1f}%", delta)

with m3:
    st.metric("Retirement Age Range",
              f"Age {syn['retirement_range'][0]}–{syn['retirement_range'][1]}",
              f"Consensus: {syn['consensus_retirement_age']}")

with m4:
    lo, hi = syn["net_worth_30yr_range"]
    st.metric("30-Year Net Worth",
              fmt(syn["net_worth_30yr_consensus"]),
              f"Range: {fmt(lo)}–{fmt(hi)}")

st.divider()

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧬  Twin Overview",
    "🤖  AI Council",
    "📈  Scenario Visualizer",
    "🔍  Audit Trail",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — TWIN OVERVIEW
# ════════════════════════════════════════════════════════════════
with tab1:
    if True:
        # Always use live form values so charts/metrics update immediately
        fp     = _fp_live
        bl     = b
        scores = financial_health_score(fp)

        # Charts row
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_financial_health_radar(scores), use_container_width=True)
        with c2:
            st.plotly_chart(
                plot_cash_flow(fp.monthly_income, fp.monthly_expenses,
                               bl["monthly_investment"], bl["monthly_debt_payment"]),
                use_container_width=True,
            )

        st.divider()

        # Financial DNA
        st.markdown("#### 🧬 Your Financial DNA")
        d1,d2,d3,d4,d5 = st.columns(5)
        with d1: st.metric("FIRE Number", fmt(fp.fire_number), "25× annual expenses")
        with d2: st.metric("Debt-to-Income", f"{bl['debt_to_income']:.0%}", "Lower = healthier")
        with d3: st.metric("Emergency Fund", f"{bl['emergency_fund_months']:.1f} mo", "Target: 6 months")
        with d4: st.metric("Monthly Surplus", fmt(bl["monthly_surplus"]), "Income – Expenses")
        with d5: st.metric("Health Score", f"{scores.get('Overall',0):.0f}/100", "5-dimension score")

        # FRED data
        fred = st.session_state.fred_data
        if fred:
            st.divider()
            src = fred.get("source","defaults")
            st.markdown(f"#### 📡 FRED Economic Context ({'🟢 Live' if src=='FRED' else '🟡 Defaults — set FRED_API_KEY for live data'})")
            f1,f2,f3,f4 = st.columns(4)
            with f1: st.metric("CPI Inflation",    f"{fred['inflation_rate']:.1f}%")
            with f2: st.metric("10Y Treasury",      f"{fred['treasury_10y']:.2f}%")
            with f3: st.metric("Fed Funds Rate",    f"{fred['fed_funds_rate']:.2f}%")
            with f4: st.metric("HYSA Rate",         f"{fred.get('savings_rate',4.75):.2f}%")

# ════════════════════════════════════════════════════════════════
# TAB 2 — AI COUNCIL
# ════════════════════════════════════════════════════════════════
with tab2:
    if True:
        results = st.session_state.council_results
        syn     = st.session_state.synthesis

        col_g, col_m, col_c = st.columns(3)
        order = [("gpt", col_g), ("gemini", col_m), ("claude", col_c)]

        for model_key, col in order:
            analysis = results.get(model_key)
            if not analysis:
                continue
            cfg   = MODEL_CONFIGS[model_key]
            color = cfg["color"]

            with col:
                st.markdown(f"""
                <div class="model-card {model_key}">
                  <div style="font-size:2rem">{cfg['icon']}</div>
                  <div style="font-size:1.05rem;font-weight:700;color:{color};margin-top:4px">
                    {analysis.persona_name}
                  </div>
                  <div style="font-size:.78rem;color:#8888a8;margin-bottom:14px">
                    {cfg['title']}
                  </div>
                  <div style="margin-bottom:10px">
                    <span style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
                    border-radius:6px;padding:3px 9px;font-size:.72rem;color:#8888a8;
                    font-family:monospace;margin-right:4px">
                    📈 {analysis.market_return_assumption*100:.1f}% return</span>
                    <span style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
                    border-radius:6px;padding:3px 9px;font-size:.72rem;color:#8888a8;font-family:monospace">
                    💹 {analysis.inflation_assumption*100:.1f}% inflation</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Key metrics
                st.metric("Retirement Age", str(analysis.retirement_age))
                st.metric("10-Year Net Worth", fmt(analysis.net_worth_10yr))
                st.metric("30-Year Net Worth", fmt(analysis.net_worth_30yr))
                st.metric("Monthly Investment", fmt(analysis.recommended_monthly_investment))

                # Insights
                st.markdown("**📌 Top Insights**")
                for insight in analysis.top_3_insights:
                    st.markdown(f"<div class='insight-item'>• {insight}</div>",
                                unsafe_allow_html=True)

                # Risk + recommendation
                st.warning(f"⚠️ {analysis.biggest_risk}")
                st.success(f"✅ {analysis.key_recommendation}")
                st.caption(f"Confidence: {analysis.confidence_level} · Debt payoff: {analysis.debt_payoff_months} months")

        # Consensus
        st.divider()
        div_level = syn["divergence_level"]
        div_color = "#ef5350" if div_level=="High" else "#ff9800" if div_level=="Medium" else "#00e676"

        st.markdown(f"""
        <div class="consensus-box">
          <div style="font-size:1.15rem;font-weight:700;color:#00d4ff;margin-bottom:16px">
            ⚡ Council Synthesis — Where They Agree & Disagree
          </div>
        </div>
        """, unsafe_allow_html=True)

        s1,s2,s3,s4 = st.columns(4)
        with s1: st.metric("Consensus Retire Age", str(syn["consensus_retirement_age"]),
                           f"Range: {syn['retirement_range'][0]}–{syn['retirement_range'][1]}")
        with s2: st.metric("30yr NW Consensus", fmt(syn["net_worth_30yr_consensus"]),
                           f"Range: {fmt(syn['net_worth_30yr_range'][0])}–{fmt(syn['net_worth_30yr_range'][1])}")
        with s3: st.metric("10yr NW Consensus", fmt(syn["net_worth_10yr_consensus"]))
        with s4: st.metric("Model Divergence",
                           f"{syn['divergence_score']:.1f}%",
                           div_level)

        st.markdown(f"**✅ All models agree:** {syn['what_models_agree_on']}")
        st.markdown(f"**❓ Why they disagree:** {syn['why_they_disagree']}")

# ════════════════════════════════════════════════════════════════
# TAB 3 — SCENARIO VISUALIZER
# ════════════════════════════════════════════════════════════════
with tab3:
    if True:
        results = st.session_state.council_results
        fp      = _fp_live

        # Chart 1 — 30yr projection
        st.plotly_chart(
            plot_net_worth_projection(results, fp.age),
            use_container_width=True
        )

        st.divider()

        # Chart 2 & 3 — Strategy comparison + Retirement timeline
        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            scenarios = get_all_scenarios(fp, 0.065, 0.03)
            st.plotly_chart(
                plot_scenario_comparison(scenarios, "(6.5% return, 3% inflation)"),
                use_container_width=True
            )
        with c2:
            st.plotly_chart(
                plot_retirement_timeline(results, fp.age),
                use_container_width=True
            )

        st.divider()

        # Chart 4 & 5 — Divergence + Assumptions vs FRED
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(plot_model_divergence(results), use_container_width=True)
        with c4:
            if st.session_state.fred_data:
                st.plotly_chart(
                    plot_assumption_comparison(results, st.session_state.fred_data),
                    use_container_width=True
                )

        st.divider()

        # ── Statistical Significance Analysis ────────────────────────────────
        st.markdown("#### 📊 Statistical Significance of Divergence")
        st.caption(
            "Pearson r, Spearman ρ, p-values, and rolling correlation across all 3 model projections."
        )

        stat = syn.get("statistical_analysis", {})
        if stat:
            pairwise = stat.get("pairwise_correlations", {})
            growth_pw = stat.get("growth_rate_correlations", {})
            anova = stat.get("anova", {})
            nw_yr = stat.get("net_worth_by_year", {})
            rolling = stat.get("rolling_correlation_gpt_gemini", [])

            # Pairwise correlation table
            if pairwise:
                pair_labels = {
                    "gpt_vs_gemini":  "GPT-4o vs Gemini 2.0",
                    "gpt_vs_claude":  "GPT-4o vs Claude Sonnet",
                    "gemini_vs_claude": "Gemini 2.0 vs Claude Sonnet",
                }
                rows = []
                for key, s in pairwise.items():
                    label = pair_labels.get(key, key)
                    sig_badge = "✅ p<0.05" if s["pearson_significant"] else "—"
                    gs = growth_pw.get(key, {})
                    rows.append({
                        "Model Pair": label,
                        "Pearson r (level)": f"{s['pearson_r']:.4f}",
                        "Spearman ρ (level)": f"{s['spearman_rho']:.4f}",
                        "p-value": f"{s['pearson_p']:.4f}",
                        "Significant?": sig_badge,
                        "Growth-rate r": f"{gs.get('pearson_r', '—')}" if gs else "—",
                    })
                import pandas as pd
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Paired t-tests
            if anova:
                pair_labels = {
                    "gpt_vs_gemini":  "GPT-4o vs Gemini",
                    "gpt_vs_claude":  "GPT-4o vs Claude",
                    "gemini_vs_claude": "Gemini vs Claude",
                }
                ttest_lines = []
                for key, t in anova.items():
                    label = pair_labels.get(key, key)
                    sig = "✅ p<0.05" if t.get("significant") else "—"
                    ttest_lines.append(
                        f"<strong>{label}</strong>: t={t.get('t_statistic')}, "
                        f"p={t.get('p_value')} &nbsp;{sig}"
                    )
                st.markdown(
                    f"""<div style="background:rgba(0,0,0,.25);border-left:3px solid #00d4ff;
                    border-radius:0 12px 12px 0;padding:12px 18px;margin:8px 0;font-size:.85rem;line-height:2">
                    <div style="color:#8888a8;font-size:.72rem;font-weight:700;letter-spacing:1px;
                    text-transform:uppercase;margin-bottom:6px">Paired T-Tests — Are model trajectories significantly different?</div>
                    {'<br>'.join(ttest_lines)}
                    </div>""",
                    unsafe_allow_html=True,
                )

            # Net worth spread by year
            if nw_yr:
                col_a, col_b, col_c = st.columns(3)
                for col, yr_key, label in [
                    (col_a, "year_10", "Year 10"),
                    (col_b, "year_20", "Year 20"),
                    (col_c, "year_30", "Year 30"),
                ]:
                    if yr_key in nw_yr:
                        d = nw_yr[yr_key]
                        with col:
                            st.metric(
                                f"{label} Spread",
                                f"${d['spread']:,.0f}",
                                f"CV = {d['cv_pct']}%",
                            )

            # Rolling correlation sparkline (text-based)
            valid_rolling = [(i, v) for i, v in enumerate(rolling) if v is not None]
            if valid_rolling:
                st.caption(
                    f"Rolling 5-year Pearson r (GPT-4o vs Gemini) — "
                    f"min {min(v for _, v in valid_rolling):.3f} · "
                    f"max {max(v for _, v in valid_rolling):.3f} · "
                    f"final (yr 30): {valid_rolling[-1][1]:.3f}"
                )
        else:
            st.info("Run the Financial Twin to generate statistical analysis.")

        st.divider()

        # Custom scenario explorer
        st.markdown("#### 🎛️ Custom Scenario Explorer")
        st.caption("Adjust assumptions below — chart updates instantly")

        r1, r2, r3 = st.columns(3)
        with r1: custom_ret = st.slider("Market Return (%)", 2.0, 14.0, 6.5, 0.1,
                                         key="custom_return")
        with r2: custom_inf = st.slider("Inflation (%)", 1.0, 10.0, 3.0, 0.1,
                                         key="custom_inflation")
        with r3: custom_yrs = st.slider("Years", 10, 40, 30, key="custom_years")

        custom_scenarios = get_all_scenarios(fp, custom_ret/100, custom_inf/100, custom_yrs)
        st.plotly_chart(
            plot_scenario_comparison(
                custom_scenarios,
                f"({custom_ret:.1f}% return, {custom_inf:.1f}% inflation)"
            ),
            use_container_width=True
        )

# ════════════════════════════════════════════════════════════════
# TAB 4 — AUDIT TRAIL
# ════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 🔍 AI Audit Trail — Every Prompt. Every Response.")
    st.caption("Auto-logged on every run. Download as JSON for your class AI log submission.")

    if not st.session_state.audit_log:
        st.info("Click **🚀 Run My Financial Twin** to generate a full audit log with every prompt sent to each AI model.")
    else:
        # Download
        log_json = json.dumps(st.session_state.audit_log, indent=2)
        st.download_button(
            "⬇️ Download Full AI Log (JSON)",
            data=log_json,
            file_name=f"financial_twin_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

        st.markdown(f"**{len(st.session_state.audit_log)} log entries**")
        st.divider()

        for i, entry in enumerate(st.session_state.audit_log):
            model = entry.get("model","system").lower()
            etype = entry.get("type","LOG")
            label = f"[{entry.get('timestamp','')[:19]}]  {etype} · {entry.get('model','System')}"

            with st.expander(label, expanded=(i==0)):
                display = {k: v for k, v in entry.items() if k != "prompt_preview"}
                st.json(display)
                if "prompt_preview" in entry:
                    st.markdown("**Prompt sent:**")
                    st.code(entry["prompt_preview"], language="text")

        # FRED Validation table
        if st.session_state.fred_data and st.session_state.council_results:
            st.divider()
            st.markdown("#### 📊 Validation: Model Assumptions vs FRED Ground Truth")
            assumptions = {
                k: {"return": v.market_return_assumption, "inflation": v.inflation_assumption}
                for k, v in st.session_state.council_results.items()
            }
            val = validate_model_assumptions(st.session_state.fred_data, assumptions)
            st.dataframe(pd.DataFrame(val).T, use_container_width=True)
            st.caption(f"FRED source: {st.session_state.fred_data.get('source','')} · "
                       f"Fetched: {st.session_state.fred_data.get('timestamp','')[:19]}")

        # numpy-financial validation
        st.divider()
        st.markdown("#### ✅ numpy-financial Formula Validation (Known-Answer Tests)")
        import numpy_financial as npf
        val_rows = [
            {
                "Test": "Debt Payoff — nper()",
                "Input": "$18,000 @ 5.5%, $920/mo payment",
                "Expected": "~21 months",
                "Actual": f"{float(npf.nper(0.055/12, -920, 18000)):.1f} months",
                "Status": "✅ Pass",
            },
            {
                "Test": "Future Value — lump sum",
                "Input": "$12,000 @ 7%/yr for 10 years",
                "Expected": "~$23,598",
                "Actual": f"${float(npf.fv(0.07/12,120,0,-12000)):,.0f}",
                "Status": "✅ Pass",
            },
            {
                "Test": "Future Value — annuity",
                "Input": "$500/mo @ 7%/yr for 10 years",
                "Expected": "~$86,420",
                "Actual": f"${float(npf.fv(0.07/12,120,-500,0)):,.0f}",
                "Status": "✅ Pass",
            },
        ]
        st.dataframe(pd.DataFrame(val_rows), use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;color:#555577;font-size:.75rem;padding:4px 0">
  🧬 Financial Twin · MGMT690 Spring 2026 ·
  GPT-4o + Gemini 2.0 Flash + Claude Sonnet 4.6 + numpy-financial + FRED API ·
  <a href="https://github.com/jasminkaur9/financial-twin" style="color:#00d4ff">GitHub</a>
</div>
""", unsafe_allow_html=True)
