# Financial Twin — Product Roadmap

**Building on:** numpy-financial, FRED API, openai + google-genai + anthropic SDKs, asyncio, Streamlit, Plotly

---

## Sections

### 1. Financial Profile Engine
User form (age, income, expenses, debt, savings, risk tolerance) + optional CSV upload → numpy-financial calculations → baseline outputs: monthly surplus, savings rate, debt payoff months, retirement age estimate, net worth trajectory. This feeds every downstream section.

### 2. Three-Model AI Council
asyncio parallel calls to GPT-4o (aggressive: 7% returns, 2.5% inflation), Gemini 2.5 Pro (conservative: 5% returns, 3.5% inflation), Claude (calibrated: 6.5% returns, 3% inflation) → each returns structured JSON advice → synthesis layer computes consensus recommendation + divergence score ("models agree on X, disagree on Y because of Z assumptions").

### 3. Twin Scenario Visualizer
Plotly interactive dashboard: 10-year + 30-year net worth projections per model (3 lines on one chart), retirement date range (earliest vs latest), scenario comparison ("pay debt first" vs "invest while in debt" vs "balanced"), model agreement heatmap. The demo screen.

### 4. Audit Dashboard + Validation
Every prompt sent and response received logged to st.session_state → in-app AI log viewer + JSON export. FRED API validation: ground-truth inflation and yield rates vs model assumptions. Validation table: numpy-financial known answers vs model outputs. Satisfies class AI log + validation requirements.

---

## Dependencies

```
Section 1 → Section 2 → Section 3
                   ↓
             Section 4 (runs throughout)
```

## Delivery Order

Build 1 → Run it → Build 2 → Run it → Build 3 → Run it → Build 4 → Polish → CI/CD

## Class Deliverables Mapping

| Requirement          | Covered By                    |
|----------------------|-------------------------------|
| Working demo         | All 4 sections running        |
| AI Log               | Section 4 (auto-logged)       |
| Validation           | Section 4 (FRED ground-truth) |
| CI/CD                | GitHub Actions (added last)   |
| Slides               | DRIVER stages = slide deck    |
| Substack Post        | Write after Section 3 demo    |
