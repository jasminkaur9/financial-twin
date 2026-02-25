"""
Visualizations — Animated Plotly charts with premium dark theme.
All charts return go.Figure objects ready for st.plotly_chart().
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

# ── Color palette ────────────────────────────────────────────────────────────
GPT_COLOR    = "#74aa9c"
GEMINI_COLOR = "#4285F4"
CLAUDE_COLOR = "#da7756"
CYAN         = "#00d4ff"
PURPLE       = "#7B2FBE"
GOLD         = "#FFD700"
GREEN        = "#00e676"
RED          = "#ef5350"

MODEL_COLORS = {"gpt": GPT_COLOR, "gemini": GEMINI_COLOR, "claude": CLAUDE_COLOR}
MODEL_LABELS = {"gpt": "GPT-4o · Alex Chen", "gemini": "Gemini · Morgan Wells", "claude": "Claude · Jordan Rivera"}

# ── Shared dark layout ────────────────────────────────────────────────────────
def _dark_layout(**overrides) -> dict:
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8e8f0", family="Inter, sans-serif", size=12),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.12)",
            linecolor="rgba(255,255,255,0.08)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.12)",
            linecolor="rgba(255,255,255,0.08)",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(size=11),
        ),
        margin=dict(t=50, b=40, l=60, r=20),
        hoverlabel=dict(
            bgcolor="rgba(20,20,40,0.95)",
            bordercolor="rgba(255,255,255,0.2)",
            font=dict(size=12),
        ),
    )
    base.update(overrides)
    return base


# ── 1. Net Worth Projection (30-year, 3 model lines) ─────────────────────────
def plot_net_worth_projection(council_results: dict, profile_age: int) -> go.Figure:
    """
    30-year net worth projection for all 3 AI models.
    Animated fade-in via Plotly's visibility toggle workaround.
    """
    fig = go.Figure()

    for model_key, analysis in council_results.items():
        projs = analysis.projections
        years = [p.year for p in projs]
        ages = [p.age for p in projs]
        nw = [p.net_worth for p in projs]

        color = MODEL_COLORS[model_key]
        label = MODEL_LABELS[model_key]

        # Confidence band (±10% for visual richness)
        nw_upper = [v * 1.10 for v in nw]
        nw_lower = [v * 0.90 for v in nw]

        # Confidence band fill
        fig.add_trace(go.Scatter(
            x=ages, y=nw_upper,
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
            fill=None, name=f"{model_key}_upper",
        ))
        fig.add_trace(go.Scatter(
            x=ages, y=nw_lower,
            mode="lines", line=dict(width=0),
            fill="tonexty",
            fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba") if "rgb" in color
                       else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)",
            showlegend=False, hoverinfo="skip",
            name=f"{model_key}_lower",
        ))

        # Main projection line
        fig.add_trace(go.Scatter(
            x=ages, y=nw,
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.8),
            marker=dict(size=4, color=color, symbol="circle"),
            hovertemplate=(
                f"<b>{label}</b><br>"
                "Age: %{x}<br>"
                "Net Worth: $%{y:,.0f}<br>"
                f"Return: {analysis.market_return_assumption*100:.1f}% | "
                f"Inflation: {analysis.inflation_assumption*100:.1f}%"
                "<extra></extra>"
            ),
        ))

    # Retirement age annotations (vertical lines)
    for model_key, analysis in council_results.items():
        fig.add_vline(
            x=analysis.retirement_age,
            line=dict(color=MODEL_COLORS[model_key], width=1, dash="dot"),
            opacity=0.4,
        )

    fig.update_layout(
        **_dark_layout(),
        title=dict(text="30-Year Net Worth Projection — AI Council", font=dict(size=16, color=CYAN)),
        xaxis_title="Age",
        yaxis_title="Net Worth ($)",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
    )
    return fig


# ── 2. Scenario Comparison (3 strategies, 1 model's assumptions) ─────────────
def plot_scenario_comparison(scenarios: Dict[str, List[Dict]], label: str = "") -> go.Figure:
    """Bar + line chart comparing 3 financial strategies at key milestones."""
    fig = go.Figure()

    colors = {"Debt First": RED, "Invest First": GREEN, "Balanced": CYAN}
    milestones = [5, 10, 15, 20, 30]

    for strategy, projs in scenarios.items():
        nw_at_milestones = []
        for m in milestones:
            row = next((p for p in projs if p["year"] == m), None)
            nw_at_milestones.append(row["net_worth"] if row else 0)

        fig.add_trace(go.Bar(
            name=strategy,
            x=[f"Year {m}" for m in milestones],
            y=nw_at_milestones,
            marker=dict(
                color=colors[strategy],
                opacity=0.8,
                line=dict(color=colors[strategy], width=1.5),
            ),
            hovertemplate=f"<b>{strategy}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        **_dark_layout(),
        title=dict(text=f"Strategy Comparison: Which Path Wins? {label}", font=dict(size=16, color=CYAN)),
        xaxis_title="Time Horizon",
        yaxis_title="Net Worth ($)",
        yaxis_tickformat="$,.0f",
        barmode="group",
        bargap=0.2,
        bargroupgap=0.05,
    )
    return fig


# ── 3. Financial Health Radar ─────────────────────────────────────────────────
def plot_financial_health_radar(scores: Dict[str, float]) -> go.Figure:
    """Spider/radar chart showing 5-dimension financial health."""
    dims = ["Savings Rate", "Emergency Fund", "Debt Load", "Investment Mix", "Cash Flow"]
    vals = [scores.get(d, 0) for d in dims]
    vals_closed = vals + [vals[0]]  # close the polygon
    dims_closed = dims + [dims[0]]

    fig = go.Figure()

    # Background reference (100%)
    fig.add_trace(go.Scatterpolar(
        r=[100] * (len(dims) + 1),
        theta=dims_closed,
        fill="toself",
        fillcolor="rgba(255,255,255,0.03)",
        line=dict(color="rgba(255,255,255,0.1)", width=1),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Actual scores
    fig.add_trace(go.Scatterpolar(
        r=vals_closed,
        theta=dims_closed,
        fill="toself",
        fillcolor="rgba(0,212,255,0.12)",
        line=dict(color=CYAN, width=2.5),
        marker=dict(size=8, color=CYAN, symbol="circle"),
        name="Your Score",
        hovertemplate="<b>%{theta}</b><br>Score: %{r:.0f}/100<extra></extra>",
    ))

    overall = scores.get("Overall", 0)
    color = GREEN if overall >= 70 else GOLD if overall >= 50 else RED

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="rgba(255,255,255,0.4)", size=9),
                gridcolor="rgba(255,255,255,0.06)",
                linecolor="rgba(255,255,255,0.06)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#e8e8f0", size=11),
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.08)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8e8f0"),
        showlegend=False,
        title=dict(
            text=f"Financial Health Score: <b style='color:{color}'>{overall:.0f}/100</b>",
            font=dict(size=15, color=CYAN),
        ),
        margin=dict(t=60, b=20, l=60, r=60),
        hoverlabel=dict(bgcolor="rgba(20,20,40,0.95)", font=dict(size=12)),
    )
    return fig


# ── 4. Model Divergence Chart ─────────────────────────────────────────────────
def plot_model_divergence(council_results: dict) -> go.Figure:
    """Horizontal bar chart showing where models agree vs diverge."""
    if not council_results:
        return go.Figure()

    metrics = {
        "Retirement Age": [a.retirement_age for a in council_results.values()],
        "10yr Net Worth ($K)": [a.net_worth_10yr / 1000 for a in council_results.values()],
        "30yr Net Worth ($K)": [a.net_worth_30yr / 1000 for a in council_results.values()],
        "Monthly Investment": [a.recommended_monthly_investment for a in council_results.values()],
    }

    model_keys = list(council_results.keys())
    model_labels = [MODEL_LABELS[k] for k in model_keys]
    colors_list = [MODEL_COLORS[k] for k in model_keys]

    fig = go.Figure()
    for i, (model_key, label, color) in enumerate(zip(model_keys, model_labels, colors_list)):
        y_vals = list(metrics.keys())
        x_vals = [
            council_results[model_key].retirement_age,
            council_results[model_key].net_worth_10yr / 1000,
            council_results[model_key].net_worth_30yr / 1000,
            council_results[model_key].recommended_monthly_investment,
        ]
        # Normalize to 0-100 for comparison
        ranges = [(55, 70), (0, max(v for vals in metrics.values() for v in vals)),
                  (0, max(v for vals in metrics.values() for v in vals)), (0, 5000)]

        fig.add_trace(go.Bar(
            name=label,
            x=[v for v in x_vals],
            y=y_vals,
            orientation="h",
            marker=dict(color=color, opacity=0.8, line=dict(color=color, width=1)),
            hovertemplate=f"<b>{label}</b><br>%{{y}}: %{{x:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        **_dark_layout(),
        title=dict(text="Model Divergence — Where Do They Disagree?", font=dict(size=16, color=CYAN)),
        barmode="group",
        xaxis_title="Value",
        yaxis_title="",
        bargap=0.3,
    )
    return fig


# ── 5. Retirement Timeline ────────────────────────────────────────────────────
def plot_retirement_timeline(council_results: dict, current_age: int) -> go.Figure:
    """Gantt-style timeline showing working years vs retirement for each model."""
    fig = go.Figure()

    today_year = 2026
    for i, (model_key, analysis) in enumerate(council_results.items()):
        retire_year = today_year + (analysis.retirement_age - current_age)
        work_years = analysis.retirement_age - current_age
        retire_years = 90 - analysis.retirement_age  # assume 90 life

        color = MODEL_COLORS[model_key]
        label = MODEL_LABELS[model_key]

        # Working phase
        fig.add_trace(go.Bar(
            name=f"{label} — Working",
            x=[work_years],
            y=[label],
            orientation="h",
            base=[0],
            marker=dict(color=color, opacity=0.5, line=dict(color=color, width=1)),
            hovertemplate=f"<b>{label}</b><br>Work until age {analysis.retirement_age}<br>{work_years} years working<extra></extra>",
            showlegend=(i == 0),
            legendgroup="working",
            legendgrouptitle_text="Working" if i == 0 else "",
        ))

        # Retirement phase
        fig.add_trace(go.Bar(
            name=f"{label} — Retired",
            x=[retire_years],
            y=[label],
            orientation="h",
            base=[work_years],
            marker=dict(
                color=color,
                opacity=0.9,
                pattern=dict(shape="/", fgcolor="rgba(255,255,255,0.3)"),
                line=dict(color=color, width=1),
            ),
            hovertemplate=f"<b>{label}</b><br>Retire at {analysis.retirement_age}<br>{retire_years} years of retirement<extra></extra>",
            showlegend=(i == 0),
            legendgroup="retired",
            legendgrouptitle_text="Retired" if i == 0 else "",
        ))

        # Retirement age annotation
        fig.add_annotation(
            x=work_years + 0.5,
            y=label,
            text=f"Age {analysis.retirement_age}",
            showarrow=False,
            font=dict(size=11, color="white", weight=700),
            bgcolor="rgba(0,0,0,0.5)",
        )

    fig.update_layout(
        **_dark_layout(),
        title=dict(text="Retirement Timeline — When Do You Stop Working?", font=dict(size=16, color=CYAN)),
        barmode="stack",
        xaxis_title="Years from Now",
        yaxis_title="",
        bargap=0.3,
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


# ── 6. Monthly Cash Flow Waterfall ───────────────────────────────────────────
def plot_cash_flow(monthly_income: float, monthly_expenses: float,
                   monthly_invest: float, monthly_debt: float) -> go.Figure:
    """Waterfall chart showing monthly money flow."""
    surplus = monthly_income - monthly_expenses
    unallocated = max(0, surplus - monthly_invest - monthly_debt)

    categories = ["Income", "Expenses", "Investment", "Debt Payment", "Unallocated"]
    values = [monthly_income, -monthly_expenses, -monthly_invest, -monthly_debt, -unallocated]
    measures = ["absolute", "relative", "relative", "relative", "relative"]
    colors = [GREEN, RED, CYAN, GOLD, "rgba(255,255,255,0.3)"]

    fig = go.Figure(go.Waterfall(
        name="Cash Flow",
        orientation="v",
        measure=measures,
        x=categories,
        y=values,
        connector=dict(line=dict(color="rgba(255,255,255,0.15)", width=1, dash="dot")),
        increasing=dict(marker=dict(color=GREEN, opacity=0.85)),
        decreasing=dict(marker=dict(color=RED, opacity=0.85)),
        totals=dict(marker=dict(color=CYAN, opacity=0.85)),
        texttemplate="$%{y:,.0f}",
        textfont=dict(color="white", size=11),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_dark_layout(),
        title=dict(text="Monthly Cash Flow Breakdown", font=dict(size=16, color=CYAN)),
        yaxis_title="Amount ($)",
        yaxis_tickformat="$,.0f",
        showlegend=False,
    )
    return fig


# ── 7. Assumption Comparison ──────────────────────────────────────────────────
def plot_assumption_comparison(council_results: dict, fred_data: dict) -> go.Figure:
    """Compare model assumptions vs FRED real-world data."""
    models = list(council_results.keys())
    labels = [MODEL_LABELS[m] for m in models] + ["FRED (Actual)"]
    returns = [council_results[m].market_return_assumption * 100 for m in models] + [float(fred_data.get("treasury_10y", 4.5))]
    inflations = [council_results[m].inflation_assumption * 100 for m in models] + [float(fred_data.get("inflation_rate", 3.1))]
    colors_list = [MODEL_COLORS[m] for m in models] + [GOLD]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Expected Return",
        x=labels,
        y=returns,
        marker=dict(color=[c for c in colors_list], opacity=0.8),
        hovertemplate="<b>%{x}</b><br>Return: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Inflation",
        x=labels,
        y=inflations,
        marker=dict(color=[c for c in colors_list], opacity=0.4,
                    pattern=dict(shape="\\", fgcolor="rgba(255,255,255,0.3)")),
        hovertemplate="<b>%{x}</b><br>Inflation: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        **_dark_layout(),
        title=dict(text="Model Assumptions vs FRED Real-World Data", font=dict(size=16, color=CYAN)),
        barmode="group",
        yaxis_title="Rate (%)",
        bargap=0.2,
    )
    return fig
