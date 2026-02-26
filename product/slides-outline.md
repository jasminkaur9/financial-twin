# Financial Twin — Slide Deck (MGMT690 Spring 2026)
# 9 Slides | Show AI DRIVER Process Explicitly

---

## SLIDE 1 — Title
**Financial Twin**
*Three AI Advisors. Three Visions of Your Financial Future. One Consensus.*

- MGMT690 Spring 2026 — Jasmin Kaur
- GitHub: github.com/jasminkaur9/financial-twin
- Built with: GPT-4o · Gemini 2.0 Flash · Claude Sonnet 4.6

Visual: Dark hero with 3 model icons + diverging projection lines

---

## SLIDE 2 — The Problem (DEFINE)
**The Gap No App Fills**

> "Every finance app shows you the PAST. None simulate your financial future across *multiple plausible realities*."

- Mint shut down 2023 — market gap
- Copilot, YNAB, Monarch Money: rule-based, single-model, no forecasting
- **What's missing:** Multi-LLM divergence — *why* experts disagree on your money

AI DRIVER Stage: DEFINE (开题调研) + 分头研究
- Research confirmed: no existing app uses multi-LLM for personal finance
- FRED API validation: real economic data, not assumptions

---

## SLIDE 3 — The Unique Idea (REPRESENT)
**The Three-Model Divergence Engine**

| Advisor | Model | Return Assumption | Inflation |
|---------|-------|-------------------|-----------|
| ⚡ Alex Chen | GPT-4o | 7.0% | 2.5% |
| 🛡️ Morgan Wells | Gemini 2.0 Flash | 5.0% | 3.5% |
| ⚖️ Jordan Rivera | Claude Sonnet 4.6 | 6.5% | 3.0% |

**Key insight:** 2% return difference → $500K+ net worth gap over 30 years
**Not three answers — three *reasoned disagreements* that teach you what matters**

AI DRIVER Stage: REPRESENT (Roadmap)
- 4 sections: Profile Engine → AI Council → Visualizer → Audit Trail

---

## SLIDE 4 — I Am the AI DRIVER
**How I Operated the AI — Not Just Copied It**

Show the DRIVER loop explicitly:
```
DEFINE → REPRESENT → IMPLEMENT → VALIDATE → EVOLVE
```

My role as the driver:
- Chose the financial domain (Personal Finance, not stocks)
- Decided "Your Financial Twin" angle over 3 other options
- Crafted distinct personas & economic assumptions for each model
- Validated model outputs against FRED ground truth
- Modified AI suggestions 12+ times based on financial logic

*"I directed the AI. The AI did not direct me."*

---

## SLIDE 5 — Live Demo Screenshot
**The App Running**

Screenshot grid (4 panels):
1. Sidebar — profile form with sliders
2. AI Council tab — 3 model cards side by side
3. 30-year projection chart — 3 diverging lines with confidence bands
4. Audit Trail — prompt log with JSON download

Key numbers from demo profile (Age 28, $6.5K income, $18K debt):
- GPT: Retire at **56** · 30yr NW: **$1.4M**
- Gemini: Retire at **63** · 30yr NW: **$870K**
- Claude: Retire at **58** · 30yr NW: **$1.15M**
- **Divergence: $530K gap — explained by 2% return assumption difference**

---

## SLIDE 6 — Technical Architecture
**Expert-Level Stack**

```
User Input (Form / CSV Upload)
        ↓
numpy-financial Engine    ←── FRED API (live CPI, Treasury yields)
        ↓
┌──────────────────────────────────────┐
│  ThreadPoolExecutor (parallel)       │
│  GPT-4o  |  Gemini 2.0  |  Claude   │  ← All 3 run simultaneously
│  instructor + Pydantic schema        │  ← Structured JSON output
└──────────────────────────────────────┘
        ↓
Synthesis Layer (consensus + divergence score)
        ↓
Plotly Dark Charts + Streamlit UI
        ↓
Audit Trail (auto-logged, JSON export)
```

CI/CD: GitHub Actions → lint + 21 validation tests on every push

---

## SLIDE 7 — Validation (VALIDATE)
**Cross-Checking My Instruments**

1. **numpy-financial known answers:**
   - $18K @ 5.5% with $920/mo → 21 months (matches formula: ✅)
   - $12K @ 7% for 10 years → $23,598 (matches tables: ✅)
   - 21/21 pytest tests passing

2. **FRED API ground truth:**
   - CPI inflation: 3.1% actual vs model range 2.5%–3.5%
   - 10Y Treasury: 4.5% vs model equity risk premiums 0.5%–2.5%
   - All model assumptions grounded in real data range

3. **Divergence makes sense:**
   - 2% return spread over 30 years = $530K difference ✅ (mathematically correct)

---

## SLIDE 8 — AI Log (Audit Trail)
**I Operated It — Here's the Evidence**

Show actual prompt sent to Claude:
> *"You are Jordan Rivera, an evidence-based financial advisor... YOUR FIXED ECONOMIC ASSUMPTIONS: Annual market return: 6.5%, Inflation: 3.0%... Client: Age 28, Income $6,500/mo, Debt $18,000 at 5.5%..."*

Show how I modified the AI:
- Iteration 1: Models gave identical answers → Fixed by enforcing different assumption sets in prompts
- Iteration 2: Gemini returned unstructured text → Added Pydantic schema + response_schema parameter
- Iteration 3: Sequential calls too slow (18s) → Switched to ThreadPoolExecutor (4s)

**Audit trail is auto-logged in the app → downloadable JSON**

---

## SLIDE 9 — What I Learned (REFLECT)
**The DRIVER Process in Practice**

✅ **What worked:**
- 分头研究 (parallel research) found `instructor` library → saved 2 hours of JSON parsing
- `google-generativeai` was deprecated → research caught it before it broke the app
- Demo mode means app works without API keys → better for class demo

⚠️ **What I'd change:**
- Start with async/await instead of ThreadPoolExecutor for cleaner parallel code
- Add streaming responses so users see AI output appear in real time

🎯 **The real insight:**
> Economic assumptions are the hidden variable in every financial forecast.
> Making them explicit and comparing them is more valuable than any single "right" answer.

GitHub: github.com/jasminkaur9/financial-twin
Substack: https://jasminkaur3.substack.com/p/i-built-a-financial-twin-using-3
