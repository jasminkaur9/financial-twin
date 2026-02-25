# Financial Twin — AI-Powered Life Scenario Simulator

## The Problem

Existing personal finance apps (Copilot, YNAB, Monarch) show you what happened to your money.
None show you what *will* happen — across multiple plausible futures, modeled by AI with different
assumptions. Mint shut down in 2023. The gap is real.

The core pain: "Should I pay off debt first or invest?" has no single answer — it depends on
assumptions about inflation, market returns, and your risk tolerance. Different experts disagree.
**Your Financial Twin makes that disagreement visible and quantified.**

## Success Looks Like

- User inputs profile (age, income, expenses, debt, savings) via form OR uploads CSV
- Three AI models (GPT-4o, Gemini Pro, Claude) each simulate 10-year and 30-year scenarios
  with **explicitly different economic assumptions**
- Side-by-side comparison: "GPT says retire at 58, Claude says 63 — here's why they disagree"
- Scenario explorer: pay-off-debt-first vs invest-while-in-debt vs balanced approach
- Final consensus recommendation with confidence interval
- Full AI log showing every prompt sent, every output received (required for class)

## How We'd Know We're Wrong

- If the FV/PV calculations don't match numpy-financial ground truth → assumption bug
- If all 3 models give identical answers → our prompting isn't enforcing different assumptions
- If users can't understand WHY models disagree → we need better UI explanation layer
- If demo takes > 30 seconds to run → parallelize API calls with asyncio

## Building On (Existing Foundations)

- **numpy-financial** — FV, PV, IRR, NPV calculations (battle-tested, Damodaran-aligned)
- **FRED API** (free) — Real inflation rates, 10Y treasury yields, savings rates
- **openai SDK** — GPT-4o calls
- **google-generativeai SDK** — Gemini Pro calls
- **anthropic SDK** — Claude calls
- **asyncio** — Parallel AI calls (all 3 run simultaneously, not sequentially)
- **Streamlit + Plotly** — Interactive dashboard, see results immediately
- **pandas** — CSV parsing, financial data manipulation

## The Unique Part

**The Three-Model Divergence Engine:**
- GPT-4o uses aggressive economic assumptions (7% market return, 2.5% inflation)
- Gemini Pro uses conservative assumptions (5% market return, 3.5% inflation)
- Claude uses historically-calibrated assumptions (6.5% market return, 3% inflation)
- Each model also interprets user behavior differently (spending patterns, discipline score)
- Result: A *range* of futures with explanation of what drives the divergence
- Fusion layer: weighted consensus + "Most Likely" scenario

No existing app shows this. This is the contribution.

## Tech Stack

- **UI:** Streamlit (Python, see results immediately, easy demo)
- **Calculations:** numpy-financial, pandas
- **AI Layer:**
  - `openai` SDK → GPT-4o / GPT-5.2
  - `google-genai` SDK → Gemini 2.5 Pro (NOT `google-generativeai` — deprecated Nov 2025)
  - `anthropic` SDK → Claude (claude-sonnet-4-6 / claude-opus-4-6)
  - `asyncio` → parallel calls, all 3 run simultaneously
- **AI Pattern:** AI Council (independent → synthesis) — 7-45% accuracy lift over single model
- **Structured Output:** `instructor` library — all 3 models return same Pydantic schema (makes divergence comparison trivial)
- **Money handling:** `numpy-financial` for FV/PV/IRR, standard float (class project scope)
- **Data:** FRED API (free), user-provided CSV or form input
- **Visualization:** Plotly (interactive charts, scenario comparison)
- **Audit Trail:** st.session_state + JSON export (class requirement: show prompts/outputs)
- **CI/CD:** GitHub Actions (lint + test on push)
- **Deployment:** Streamlit Community Cloud (free, one-click deploy)

## Open Questions

- How to handle users without API keys? (Mock mode with pre-computed responses for demo)
- FRED API: which series exactly? (CPIAUCSL for inflation, DGS10 for 10Y yield, APY for savings)
- CSV format: support Mint export format (defunct but users still have the data)?

## Deliverables (Class Requirements)

- [ ] Public GitHub repo with README + data + AI log
- [ ] Working Streamlit app (demo)
- [ ] 5-10 slide deck showing AI DRIVER process
- [ ] Substack post
- [ ] Validation documentation
- [ ] CI/CD pipeline (GitHub Actions)

**Due: Mar 2, 2026 11:59 PM**
