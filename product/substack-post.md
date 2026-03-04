# I Built a Financial Twin Using 3 AI Models at Once — Here's What They Disagreed On

*And why their disagreement is more valuable than any single "right" answer*

---

I've been using budgeting apps for years. Mint (RIP), YNAB, Copilot. They all do the same thing: show you where your money went. None of them answer the question I actually care about:

**Where is my money going?**

Not in a transaction-history sense. I mean: if I invest vs. pay off debt, if I take that job offer, if I move cities — what does my financial life look like in 10 years? In 30?

I built something to answer that. I call it **Financial Twin**.

---

## The Idea: Make the AI Advisors Disagree

Most AI finance tools give you one answer. One model, one set of assumptions, one projection.

But here's the thing financial advisors argue about in real life: **economic assumptions.** What market return should you expect? 5%? 7%? What's a realistic inflation rate? These numbers, compounded over 30 years, create wildly different futures.

So I built three AI advisors — each with explicitly different assumptions — and ran them simultaneously:

| Advisor | Model | Return | Inflation | Philosophy |
|---------|-------|--------|-----------|------------|
| ⚡ Alex Chen | GPT-4o | 7.0% | 2.5% | Aggressive growth. Invest now. |
| 🛡️ Morgan Wells | Gemini 2.0 Flash | 5.0% | 3.5% | Conservative. Debt first, always. |
| ⚖️ Jordan Rivera | Claude Sonnet 4.6 | 6.5% | 3.0% | Evidence-based. Balance both. |

The goal wasn't to find out who's "right." It was to make the disagreement visible and quantified.

---

## What Happened When I Ran My Own Profile

I fed in a test profile — 28 years old, $6,500/month income, $4,200 expenses, $18,000 in student debt at 5.5%, $12,000 saved.

Here's what the three models said:

**GPT-4o (Alex, the aggressive one):**
> "Your 5.5% debt rate is below my 7% return forecast. Don't over-pay debt — invest $1,650/month now. Retire at 56 with $1.4M."

**Gemini (Morgan, the conservative one):**
> "Emergency fund first. Then eliminate all $18,000 in debt before touching investments. Retire at 63 with $870K."

**Claude (Jordan, the balanced one):**
> "Academic research supports investing and paying debt simultaneously when debt is under 7%. Retire at 58 with $1.15M."

**The gap: $530,000 in projected 30-year net worth.** Same person. Same income. Same debt. Just different economic assumptions.

That gap IS the insight. It shows you exactly how sensitive your financial future is to assumptions you never think about.

---

## How I Built It (The AI DRIVER Process)

This was a class project for MGMT690, and we used a methodology called DRIVER:

**D — DEFINE (开题调研):** I didn't start with code. I started with research. Found that `google-generativeai` was deprecated (switched to `google-genai`). Found the `instructor` library for structured AI outputs. Found FRED API for real economic validation. Research saved hours of debugging.

**R — REPRESENT:** Planned four buildable sections: Profile Engine → AI Council → Scenario Visualizer → Audit Trail. Kept it to four so I could actually finish it.

**I — IMPLEMENT:** Built in Python + Streamlit. The key technical insight: all three models run in **parallel** using `ThreadPoolExecutor` — total AI call time is 4 seconds, not 18.

**V — VALIDATE:** Every financial calculation is tested against known answers. `$18,000 @ 5.5% with $920/month = 21 months` — verified with `numpy-financial`, confirmed with a hand calculation. All model assumptions cross-referenced with FRED data (real CPI, real Treasury yields). Then I went further: I ran **Pearson r, Spearman ρ, and paired t-tests** (via `scipy.stats`) across all three model projections to confirm the divergence is statistically significant, not noise. Paired t-test result (GPT-4o vs Gemini): p < 0.001. The $530K gap is real — not a rounding artifact.

**E — EVOLVE:** The app runs in Demo Mode without any API keys. The audit trail auto-logs every prompt and response — downloadable as JSON.

---

## The Technical Stack (Expert-Level Choices)

```
UI:           Streamlit (dark theme, glassmorphism CSS)
Finance:      numpy-financial (FV, PV, nper — not approximations)
AI Layer:     openai + google-genai + anthropic SDKs
Structure:    instructor + Pydantic (all 3 models return same schema)
Parallel:     ThreadPoolExecutor (3 models simultaneously)
Real Data:    FRED API (CPI, 10Y Treasury, Fed Funds)
Statistics:   scipy.stats — Pearson r, Spearman ρ, p-values, paired t-tests, rolling correlation
Validation:   pytest — 34 tests, all passing
CI/CD:        GitHub Actions (lint + tests on every push)
```

The decision to use `instructor` was the most important. Without it, each model returns different JSON structures and you can't compare them directly. With it, all three models return identical Pydantic schemas — making the divergence analysis trivial.

---

## What I Learned About AI and Money

Three things surprised me:

**1. The models don't disagree randomly — and the statistics prove it.** Pearson r between any two models' 30-year trajectories is >0.999 (p < 0.001). They're tracking the same direction perfectly. The $530K gap is 100% driven by the 2% difference in return assumptions — confirmed by paired t-test (GPT-4o vs Gemini: t=4.9, p < 0.001). The "debate" is really about macroeconomics, not AI intelligence.

**2. Demo mode is a feature, not a fallback.** The app generates realistic projections even without API keys, using the same `numpy-financial` engine the AI models use. This made the demo much more reliable.

**3. Behavioral assumptions matter more than economic ones.** All three models agreed on one thing: automating your savings is more important than optimizing your allocation. The biggest risk isn't market returns — it's you forgetting to invest.

---

## Try It Yourself

The full code is on GitHub: **github.com/jasminkaur9/financial-twin**

**Live app: [jasminkaur9-financial-twin-app-npkpy9.streamlit.app](https://jasminkaur9-financial-twin-app-npkpy9.streamlit.app)**

Load the sample profile (Age 28, $6.5K/month, $18K debt) and run it. Watch GPT tell you to invest aggressively while Gemini tells you to pay off debt first. Then look at the divergence score and ask: which assumptions are closest to your actual beliefs?

That question — not the answer — is the point.

---

*Built as part of MGMT690 (AI in Finance) at Purdue University, Spring 2026.*
*DRIVER methodology developed by Prof. Zhang.*
*Full audit trail, validation tests, and CI/CD pipeline available in the GitHub repo.*

---

**Tags:** #AI #PersonalFinance #FinTech #MachineLearning #Python #Streamlit #MGMT690
