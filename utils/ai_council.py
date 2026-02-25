"""
AI Council — Parallel multi-model financial analysis.
GPT-4o (Aggressive) | Gemini 2.0 Flash (Conservative) | Claude Sonnet (Balanced)

Pattern: ThreadPoolExecutor → all 3 models run simultaneously.
Structured output: instructor (GPT + Claude), response_schema (Gemini).
Falls back to demo results if API keys are not set.
"""

import os
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


# ── Pydantic Schema (shared across all 3 models) ─────────────────────────────

class YearlyProjection(BaseModel):
    year: int
    age: int
    savings: float
    debt: float
    net_worth: float


class FinancialAnalysis(BaseModel):
    persona_name: str = Field(description="Advisor persona name, e.g. 'Alex Chen'")
    model_id: str = Field(description="gpt | gemini | claude")
    market_return_assumption: float = Field(description="Annual market return as decimal, e.g. 0.07")
    inflation_assumption: float = Field(description="Annual inflation as decimal, e.g. 0.025")
    debt_payoff_months: int = Field(description="Months to pay off all debt")
    retirement_age: int = Field(description="Age when portfolio hits 25x annual expenses (FIRE)")
    net_worth_10yr: float = Field(description="Projected net worth in 10 years")
    net_worth_30yr: float = Field(description="Projected net worth in 30 years")
    recommended_monthly_investment: float = Field(description="Monthly investment recommendation")
    recommended_monthly_debt_payment: float = Field(description="Monthly debt payment recommendation")
    top_3_insights: List[str] = Field(description="Three specific actionable insights", min_length=3, max_length=3)
    biggest_risk: str = Field(description="Single most important financial risk")
    key_recommendation: str = Field(description="Most important action (1-2 sentences)")
    confidence_level: str = Field(description="High | Medium | Low")
    projections: List[YearlyProjection] = Field(description="Year-by-year projections, year 0 through 30")


# ── Model Configurations ──────────────────────────────────────────────────────

MODEL_CONFIGS = {
    "gpt": {
        "color": "#74aa9c", "icon": "⚡",
        "persona": "Alex Chen", "title": "Growth Optimizer",
        "market_return": 0.07, "inflation": 0.025,
        "philosophy": (
            "Time in market beats timing the market. Invest aggressively now. "
            "Pay only minimums on debt with interest below 7% — the market return spread is your profit."
        ),
    },
    "gemini": {
        "color": "#4285F4", "icon": "🛡️",
        "persona": "Morgan Wells", "title": "Safety Architect",
        "market_return": 0.05, "inflation": 0.035,
        "philosophy": (
            "I've seen three recessions. Build 6-month emergency fund first, "
            "eliminate all debt before investing. Conservative 5% return prevents disappointment. "
            "Cash flow freedom is more valuable than portfolio size."
        ),
    },
    "claude": {
        "color": "#da7756", "icon": "⚖️",
        "persona": "Jordan Rivera", "title": "Evidence-Based Planner",
        "market_return": 0.065, "inflation": 0.03,
        "philosophy": (
            "Academic research supports 6.5% long-run equity returns (Vanguard forecast). "
            "Pay down high-interest debt first; invest simultaneously for debt under 7%. "
            "Automate everything — behavioral consistency beats optimization."
        ),
    },
}


# ── Prompt Builder ────────────────────────────────────────────────────────────

def _build_prompt(profile: dict, model_key: str) -> str:
    cfg = MODEL_CONFIGS[model_key]
    surplus = profile["monthly_income"] - profile["monthly_expenses"]
    fire_number = profile["monthly_expenses"] * 12 * 25

    return f"""You are {cfg['persona']}, a financial advisor with this philosophy:
"{cfg['philosophy']}"

YOUR FIXED ECONOMIC ASSUMPTIONS (use exactly these numbers in all calculations):
- Annual market return: {cfg['market_return']*100:.1f}%
- Annual inflation rate: {cfg['inflation']*100:.1f}%

CLIENT PROFILE:
- Age: {profile['age']}
- Monthly Income: ${profile['monthly_income']:,.0f}
- Monthly Expenses: ${profile['monthly_expenses']:,.0f}
- Monthly Surplus: ${surplus:,.0f}
- Total Debt: ${profile['total_debt']:,.0f} at {profile['debt_rate']*100:.1f}% annual interest
- Current Savings/Investments: ${profile['savings']:,.0f}
- Current Net Worth: ${profile['savings'] - profile['total_debt']:,.0f}
- Risk Tolerance: {profile['risk_tolerance']}
- FIRE Number (25x annual expenses): ${fire_number:,.0f}

Analyze this client using YOUR specific {cfg['market_return']*100:.1f}% return assumption.
Your projections MUST differ from other advisors who use different assumptions.
Provide year-by-year projections for years 0 through 30.
Set persona_name to "{cfg['persona']}" and model_id to "{model_key}".
Be specific, direct, and actionable. Use real dollar amounts, not percentages alone."""


# ── Individual Model Callers ──────────────────────────────────────────────────

def _call_gpt(profile: dict, audit_log: list) -> Optional[FinancialAnalysis]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        import instructor
        from openai import OpenAI

        client = instructor.from_openai(OpenAI(api_key=api_key))
        prompt = _build_prompt(profile, "gpt")
        t0 = time.time()

        result = client.chat.completions.create(
            model="gpt-4o",
            response_model=FinancialAnalysis,
            messages=[
                {"role": "system", "content": "You are a financial advisor. Return precise structured data."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
            temperature=0.3,
        )
        elapsed = round(time.time() - t0, 2)

        audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "AI_CALL",
            "model": "GPT-4o",
            "persona": "Alex Chen (Growth Optimizer)",
            "assumptions": {"return": "7.0%", "inflation": "2.5%"},
            "prompt_chars": len(prompt),
            "prompt_preview": prompt[:600] + "...",
            "response_retirement_age": result.retirement_age,
            "response_nw_30yr": result.net_worth_30yr,
            "response_recommendation": result.key_recommendation,
            "elapsed_seconds": elapsed,
        })
        return result

    except Exception as e:
        audit_log.append({"timestamp": datetime.now().isoformat(), "model": "GPT-4o", "error": str(e)})
        return None


def _call_gemini(profile: dict, audit_log: list) -> Optional[FinancialAnalysis]:
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = _build_prompt(profile, "gemini")
        t0 = time.time()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FinancialAnalysis,
                temperature=0.3,
            ),
        )
        elapsed = round(time.time() - t0, 2)
        result = FinancialAnalysis.model_validate_json(response.text)

        audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "AI_CALL",
            "model": "Gemini 2.0 Flash",
            "persona": "Morgan Wells (Safety Architect)",
            "assumptions": {"return": "5.0%", "inflation": "3.5%"},
            "prompt_chars": len(prompt),
            "prompt_preview": prompt[:600] + "...",
            "response_retirement_age": result.retirement_age,
            "response_nw_30yr": result.net_worth_30yr,
            "response_recommendation": result.key_recommendation,
            "elapsed_seconds": elapsed,
        })
        return result

    except Exception as e:
        audit_log.append({"timestamp": datetime.now().isoformat(), "model": "Gemini", "error": str(e)})
        return None


def _call_claude(profile: dict, audit_log: list) -> Optional[FinancialAnalysis]:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    try:
        import instructor
        from anthropic import Anthropic

        client = instructor.from_anthropic(Anthropic(api_key=api_key))
        prompt = _build_prompt(profile, "claude")
        t0 = time.time()

        result = client.messages.create(
            model="claude-sonnet-4-6",
            response_model=FinancialAnalysis,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        elapsed = round(time.time() - t0, 2)

        audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "AI_CALL",
            "model": "Claude Sonnet 4.6",
            "persona": "Jordan Rivera (Evidence-Based Planner)",
            "assumptions": {"return": "6.5%", "inflation": "3.0%"},
            "prompt_chars": len(prompt),
            "prompt_preview": prompt[:600] + "...",
            "response_retirement_age": result.retirement_age,
            "response_nw_30yr": result.net_worth_30yr,
            "response_recommendation": result.key_recommendation,
            "elapsed_seconds": elapsed,
        })
        return result

    except Exception as e:
        audit_log.append({"timestamp": datetime.now().isoformat(), "model": "Claude", "error": str(e)})
        return None


# ── Parallel Runner ────────────────────────────────────────────────────────────

def run_council(profile: dict, audit_log: list) -> Dict[str, FinancialAnalysis]:
    """
    Run all 3 models in parallel via ThreadPoolExecutor.
    Returns {model_key: FinancialAnalysis}. Missing → demo fallback.
    """
    results = {}

    audit_log.append({
        "timestamp": datetime.now().isoformat(),
        "type": "COUNCIL_START",
        "note": "Launching GPT-4o, Gemini 2.0 Flash, Claude Sonnet in parallel",
        "profile_summary": {
            "age": profile["age"],
            "monthly_income": profile["monthly_income"],
            "monthly_expenses": profile["monthly_expenses"],
            "total_debt": profile["total_debt"],
            "savings": profile["savings"],
        },
    })

    callers = {"gpt": _call_gpt, "gemini": _call_gemini, "claude": _call_claude}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fn, profile, audit_log): key for key, fn in callers.items()}
        for future in as_completed(futures, timeout=120):
            key = futures[future]
            try:
                result = future.result()
                if result is not None:
                    results[key] = result
            except Exception as e:
                audit_log.append({"timestamp": datetime.now().isoformat(), "model": key, "error": str(e)})

    # Demo fallback for any missing models
    missing = [k for k in ["gpt", "gemini", "claude"] if k not in results]
    if missing:
        demo = _generate_demo(profile)
        for k in missing:
            results[k] = demo[k]
        audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "DEMO_MODE",
            "models_using_demo": missing,
            "reason": "API key not configured. Set OPENAI_API_KEY / GOOGLE_API_KEY / ANTHROPIC_API_KEY in .env",
        })

    audit_log.append({
        "timestamp": datetime.now().isoformat(),
        "type": "COUNCIL_COMPLETE",
        "models_returned": list(results.keys()),
        "retirement_ages": {k: v.retirement_age for k, v in results.items()},
        "nw_30yr": {k: v.net_worth_30yr for k, v in results.items()},
    })

    return results


# ── Synthesis ─────────────────────────────────────────────────────────────────

def synthesize_council(results: Dict[str, FinancialAnalysis]) -> dict:
    """
    Compute consensus + divergence across all 3 models.
    Divergence = coefficient of variation (std/mean * 100).
    """
    analyses = list(results.values())

    def cv(data):
        m = statistics.mean(data)
        return (statistics.stdev(data) / abs(m) * 100) if len(data) > 1 and m != 0 else 0

    ages = [a.retirement_age for a in analyses]
    nw10 = [a.net_worth_10yr for a in analyses]
    nw30 = [a.net_worth_30yr for a in analyses]
    returns = [a.market_return_assumption for a in analyses]
    inflations = [a.inflation_assumption for a in analyses]

    div = round((cv(ages) + cv(nw10) + cv(nw30)) / 3, 1)

    return {
        "consensus_retirement_age": round(sum(ages) / len(ages)),
        "retirement_range": (min(ages), max(ages)),
        "net_worth_10yr_consensus": round(sum(nw10) / len(nw10)),
        "net_worth_10yr_range": (round(min(nw10)), round(max(nw10))),
        "net_worth_30yr_consensus": round(sum(nw30) / len(nw30)),
        "net_worth_30yr_range": (round(min(nw30)), round(max(nw30))),
        "divergence_score": div,
        "divergence_level": "High" if div > 25 else "Medium" if div > 10 else "Low",
        "assumption_return_range": (f"{min(returns)*100:.1f}%", f"{max(returns)*100:.1f}%"),
        "assumption_inflation_range": (f"{min(inflations)*100:.1f}%", f"{max(inflations)*100:.1f}%"),
        "what_models_agree_on": (
            "Automate investments immediately. Build emergency fund. Avoid lifestyle inflation."
        ),
        "why_they_disagree": (
            f"Return assumptions span {min(returns)*100:.1f}%–{max(returns)*100:.1f}%. "
            f"Inflation assumptions span {min(inflations)*100:.1f}%–{max(inflations)*100:.1f}%. "
            f"Over 30 years, compounding magnifies these into a "
            f"${max(nw30)-min(nw30):,.0f} net worth gap."
        ),
    }


# ── Demo Generator ────────────────────────────────────────────────────────────

def _generate_demo(profile: dict) -> Dict[str, FinancialAnalysis]:
    """
    Generate demo results using our own financial engine (no API calls).
    Produces realistic, divergent outputs that look and feel like real AI analysis.
    """
    from utils.financial_engine import (
        FinancialProfile, project_net_worth, estimate_retirement_age, months_to_debt_payoff
    )

    fp = FinancialProfile(
        age=profile["age"],
        monthly_income=profile["monthly_income"],
        monthly_expenses=profile["monthly_expenses"],
        total_debt=profile["total_debt"],
        debt_interest_rate=profile["debt_rate"],
        current_savings=profile["savings"],
        risk_tolerance=profile["risk_tolerance"],
    )
    surplus = fp.monthly_surplus

    configs_demo = {
        "gpt": (
            0.07, 0.025, "Alex Chen", "⚡",
            f"Invest ${round(surplus*0.75):,}/month immediately into low-cost index funds. "
            f"Your 5.5% debt rate is below expected 7% market return — don't over-pay debt.",
            "Behavioral risk: panic-selling in downturns will destroy compound growth advantage.",
            [
                f"With ${surplus:,.0f}/month surplus, invest ${round(surplus*0.75):,} — your debt rate is below market returns",
                f"FIRE number: ${fp.fire_number:,.0f} — aggressive investing gets you there faster",
                "S&P 500 7-year rolling returns have never been negative — stay invested",
            ],
        ),
        "gemini": (
            0.05, 0.035, "Morgan Wells", "🛡️",
            f"Pay off ${fp.total_debt:,.0f} in debt first, then redirect all ${surplus:,.0f} to investments. "
            "Debt payoff is a guaranteed 5.5% return — better than my 5% market forecast.",
            "Sequence-of-returns risk: investing before clearing debt doubles your exposure in a downturn.",
            [
                f"Emergency fund target: ${fp.monthly_expenses*6:,.0f} — you currently have {fp.emergency_fund_months:.1f} months",
                "Conservative 5% return means debt payoff outperforms investing on risk-adjusted basis",
                f"Inflation at 3.5% erodes ${round(fp.monthly_income*0.12*0.035*12):,}/year of purchasing power — prioritize cash flow",
            ],
        ),
        "claude": (
            0.065, 0.03, "Jordan Rivera", "⚖️",
            f"Allocate ${round(surplus*0.6):,}/month to index funds + ${round(surplus*0.4):,} to debt simultaneously. "
            "Academic research (Vanguard 2025) supports this split for your debt rate.",
            "Behavioral drag: manual transfers lead to inconsistency. Automate all allocations.",
            [
                f"FIRE number ${fp.fire_number:,.0f} achievable by {estimate_retirement_age(fp, 0.065, 0.03)} (Vanguard 6.5% forecast)",
                f"Debt at 5.5% vs 6.5% market return: ${round(surplus*0.4):,}/month debt payoff = guaranteed 5.5% return",
                "Automate: direct deposit split ensures behavioral consistency — the biggest determinant of wealth",
            ],
        ),
    }

    results = {}
    for model_key, (ret, inf, persona, icon, rec, risk, insights) in configs_demo.items():
        projs_raw = project_net_worth(fp, ret, inf, "balanced", 30)
        debt_months = months_to_debt_payoff(fp.total_debt, fp.debt_interest_rate, surplus * 0.4)
        retire_age = estimate_retirement_age(fp, ret, inf)

        projections = [
            YearlyProjection(
                year=p["year"], age=p["age"],
                savings=p["savings"], debt=p["debt"], net_worth=p["net_worth"],
            )
            for p in projs_raw
        ]
        nw10 = projs_raw[10]["net_worth"] if len(projs_raw) > 10 else 0
        nw30 = projs_raw[30]["net_worth"] if len(projs_raw) > 30 else 0

        results[model_key] = FinancialAnalysis(
            persona_name=persona,
            model_id=model_key,
            market_return_assumption=ret,
            inflation_assumption=inf,
            debt_payoff_months=debt_months,
            retirement_age=retire_age,
            net_worth_10yr=nw10,
            net_worth_30yr=nw30,
            recommended_monthly_investment=round(surplus * 0.6 if model_key != "gemini" else surplus * 0.2),
            recommended_monthly_debt_payment=round(surplus * 0.4 if model_key != "gemini" else surplus * 0.8),
            top_3_insights=insights,
            biggest_risk=risk,
            key_recommendation=rec,
            confidence_level="High" if model_key == "claude" else "Medium",
            projections=projections,
        )

    return results
