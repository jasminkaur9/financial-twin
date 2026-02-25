# 🧬 Financial Twin — AI-Powered Life Scenario Simulator

> Three AI advisors. Three visions of your financial future. One consensus.

**MGMT690 · Spring 2026 · Jasmin Kaur**

[![CI/CD](https://github.com/your-username/financial-twin/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/financial-twin/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31-red)](https://streamlit.io)

---

## What It Does

Financial Twin runs your financial profile through **three frontier AI models simultaneously**, each with explicitly different economic assumptions:

| AI Advisor | Persona | Return Assumption | Inflation |
|-----------|---------|-------------------|-----------|
| ⚡ GPT-4o | Alex Chen — Growth Optimizer | 7.0% | 2.5% |
| 🛡️ Gemini 2.0 Flash | Morgan Wells — Safety Architect | 5.0% | 3.5% |
| ⚖️ Claude Sonnet 4.6 | Jordan Rivera — Evidence-Based Planner | 6.5% | 3.0% |

The result: a **quantified divergence** showing not just *what* happens, but *why* the models disagree — and what drives the difference in your 30-year net worth projection.

## Live Demo

👉 [**Launch App — Financial Twin**](https://jasminkaur9-financial-twin-app-npkpy9.streamlit.app)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-username/financial-twin.git
cd financial-twin

# 2. Install
pip install -r requirements.txt

# 3. Configure API keys (optional — runs in Demo Mode without them)
cp .env.example .env
# Edit .env with your keys

# 4. Run
streamlit run app.py
```

## AI Log

All prompts, responses, and model outputs are automatically logged in the **Audit Trail** tab.
Download the full JSON log for your AI log submission.

## Validation

- All financial calculations use `numpy-financial` (FV, PV, nper)
- Known-answer tests in `tests/test_financial_engine.py`
- FRED API validation: model assumptions compared against real CPI and Treasury yields
- Run: `pytest tests/ -v`

## Project Structure

```
financial-twin/
├── app.py                    # Main Streamlit app
├── utils/
│   ├── financial_engine.py   # numpy-financial calculations
│   ├── ai_council.py         # Parallel AI calls (GPT + Gemini + Claude)
│   ├── visualizations.py     # Plotly dark-theme charts
│   └── data_fetcher.py       # FRED API integration
├── tests/
│   └── test_financial_engine.py  # Validation tests
├── .github/workflows/ci.yml  # CI/CD pipeline
├── product/
│   ├── product-overview.md   # DRIVER definition
│   └── product-roadmap.md    # DRIVER roadmap
└── requirements.txt
```

## Tech Stack

- **UI**: Streamlit + custom CSS (glassmorphism dark theme)
- **Charts**: Plotly (animated, dark)
- **AI**: OpenAI SDK + google-genai SDK + Anthropic SDK + instructor
- **Parallel**: ThreadPoolExecutor (all 3 models run simultaneously)
- **Finance**: numpy-financial, pandas
- **Data**: FRED API (free economic data)
- **CI/CD**: GitHub Actions

## DRIVER Methodology

This project follows the **DRIVER** (Define → Represent → Implement → Validate → Evolve → Reflect) methodology developed in MGMT690.

**AI Log requirement**: The Audit Trail tab logs every prompt sent to every model, every response received, and all modifications made during development. Export via the Download button.

## Class Deliverables

- [x] Public GitHub repo
- [x] Working demo (Streamlit app)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Validation (numpy-financial known answers + FRED data)
- [x] AI Log (built-in Audit Trail + JSON export)
- [ ] Slides (5-10 slides showing DRIVER stages)
- [ ] Substack post

## Data Sources

- **FRED API** (Federal Reserve Economic Data) — CPI inflation, 10-Year Treasury, Fed Funds Rate
- **User input** — Form or CSV upload
- No API keys needed for demo mode

## Security

API keys are loaded from `.env` (not committed). CI/CD includes a secrets scan that fails the build if keys are accidentally exposed.

---

*Built with Claude Code + DRIVER methodology · MGMT690 Spring 2026*
