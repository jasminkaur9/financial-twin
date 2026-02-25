"""
Financial Engine — Core calculations using numpy-financial.
All formulas are academically validated. See tests/ for known-answer verification.
"""

import numpy_financial as npf
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass
class FinancialProfile:
    age: int
    monthly_income: float
    monthly_expenses: float
    total_debt: float
    debt_interest_rate: float   # Annual, e.g. 0.055
    current_savings: float
    risk_tolerance: str = "moderate"  # conservative | moderate | aggressive

    @property
    def monthly_surplus(self) -> float:
        return self.monthly_income - self.monthly_expenses

    @property
    def annual_income(self) -> float:
        return self.monthly_income * 12

    @property
    def savings_rate(self) -> float:
        return self.monthly_surplus / self.monthly_income if self.monthly_income > 0 else 0

    @property
    def net_worth(self) -> float:
        return self.current_savings - self.total_debt

    @property
    def debt_to_income(self) -> float:
        return self.total_debt / self.annual_income if self.annual_income > 0 else 0

    @property
    def emergency_fund_months(self) -> float:
        return self.current_savings / self.monthly_expenses if self.monthly_expenses > 0 else 0

    @property
    def fire_number(self) -> float:
        """FIRE number: 25x annual expenses (4% withdrawal rule)"""
        return self.monthly_expenses * 12 * 25


def months_to_debt_payoff(principal: float, annual_rate: float, monthly_payment: float) -> int:
    """
    Months to pay off debt using numpy-financial nper().
    Validated: $18,000 @ 5.5% with $920/mo ≈ 21 months.
    """
    if principal <= 0:
        return 0
    if monthly_payment <= 0:
        return 9999
    monthly_rate = annual_rate / 12
    try:
        months = npf.nper(monthly_rate, -monthly_payment, principal)
        if np.isnan(months) or np.isinf(months):
            return 9999
        return max(0, int(np.ceil(float(months))))
    except Exception:
        return 9999


def future_value(present_value: float, monthly_contribution: float,
                 annual_return: float, years: int) -> float:
    """
    Future value = FV of lump sum + FV of monthly contributions.
    Uses numpy-financial fv() for both components.
    """
    if years == 0:
        return present_value
    monthly_rate = annual_return / 12
    n = years * 12
    fv_lump = float(npf.fv(monthly_rate, n, 0, -present_value))
    fv_annuity = float(npf.fv(monthly_rate, n, -monthly_contribution, 0))
    return fv_lump + fv_annuity


def estimate_retirement_age(profile: FinancialProfile, annual_return: float = 0.065,
                             inflation_rate: float = 0.03) -> int:
    """Estimate retirement age when savings hit FIRE number (25x annual expenses)."""
    fire_number = profile.fire_number
    monthly_invest = profile.monthly_surplus * 0.60
    if monthly_invest <= 0:
        return 99
    for years in range(1, 51):
        projected = future_value(profile.current_savings, monthly_invest, annual_return, years)
        if projected >= fire_number:
            return profile.age + years
    return 99


def calculate_baseline(profile: FinancialProfile) -> Dict:
    """Calculate baseline financial metrics from profile."""
    monthly_debt_pay = max(
        profile.monthly_income * 0.10,
        min(profile.monthly_surplus * 0.5, profile.monthly_surplus)
    ) if profile.total_debt > 0 else 0

    debt_months = months_to_debt_payoff(
        profile.total_debt, profile.debt_interest_rate, monthly_debt_pay
    )
    monthly_invest = max(0, profile.monthly_surplus - monthly_debt_pay)

    return {
        "monthly_surplus": profile.monthly_surplus,
        "savings_rate_pct": round(profile.savings_rate * 100, 1),
        "net_worth": profile.net_worth,
        "debt_payoff_months": debt_months,
        "monthly_debt_payment": monthly_debt_pay,
        "monthly_investment": monthly_invest,
        "emergency_fund_months": round(profile.emergency_fund_months, 1),
        "fire_number": profile.fire_number,
        "debt_to_income": round(profile.debt_to_income, 2),
    }


def project_net_worth(profile: FinancialProfile, annual_return: float = 0.065,
                      inflation_rate: float = 0.03, strategy: str = "balanced",
                      years: int = 30) -> List[Dict]:
    """
    Year-by-year net worth projection.
    strategy: debt_first | invest_first | balanced
    Uses monthly compounding for accuracy.
    """
    projections = []
    savings = profile.current_savings
    debt = profile.total_debt
    surplus = profile.monthly_surplus
    r_invest = annual_return / 12
    r_debt = profile.debt_interest_rate / 12

    for year in range(years + 1):
        nw = savings - debt
        projections.append({
            "year": year,
            "age": profile.age + year,
            "savings": round(savings, 0),
            "debt": round(debt, 0),
            "net_worth": round(nw, 0),
            "real_net_worth": round(nw / ((1 + inflation_rate) ** year), 0),
        })
        if year >= years:
            break

        # Allocation
        if strategy == "debt_first":
            m_invest = 0 if debt > 0 else surplus
            m_debt = surplus if debt > 0 else 0
        elif strategy == "invest_first":
            m_invest = surplus * 0.85
            m_debt = surplus * 0.15
        else:  # balanced
            m_invest = surplus * 0.60
            m_debt = surplus * 0.40

        for _ in range(12):
            savings = savings * (1 + r_invest) + m_invest
            if debt > 0:
                interest = debt * r_debt
                principal = max(0, m_debt - interest)
                debt = max(0, debt - principal)
                if debt == 0 and strategy == "debt_first":
                    m_invest = surplus
                    m_debt = 0

    return projections


def get_all_scenarios(profile: FinancialProfile, annual_return: float,
                      inflation_rate: float, years: int = 30) -> Dict[str, List[Dict]]:
    """Return all 3 strategy projections for given assumptions."""
    return {
        "Debt First": project_net_worth(profile, annual_return, inflation_rate, "debt_first", years),
        "Invest First": project_net_worth(profile, annual_return, inflation_rate, "invest_first", years),
        "Balanced": project_net_worth(profile, annual_return, inflation_rate, "balanced", years),
    }


def financial_health_score(profile: FinancialProfile) -> Dict[str, float]:
    """
    5-dimension financial health score (0–100 each).
    Benchmarks: savings rate 20%, emergency fund 6mo, debt load 0 DTI,
    investment mix 100% savings, cash flow 30% surplus.
    """
    sr = profile.savings_rate * 100
    em = profile.emergency_fund_months
    dti = profile.debt_to_income
    total = profile.current_savings + profile.total_debt
    invest_mix = (profile.current_savings / total * 100) if total > 0 else 100

    scores = {
        "Savings Rate":    min(100.0, (sr / 20) * 100),
        "Emergency Fund":  min(100.0, (em / 6) * 100),
        "Debt Load":       max(0.0, 100 - dti * 100),
        "Investment Mix":  invest_mix,
        "Cash Flow":       min(100.0, (sr / 30) * 100),
    }
    weights = [0.25, 0.20, 0.20, 0.15, 0.20]
    overall = sum(v * w for v, w in zip(scores.values(), weights))
    scores["Overall"] = round(overall, 1)
    return {k: round(v, 1) for k, v in scores.items()}
