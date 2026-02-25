"""
Validation tests for financial_engine.py.
Tests known answers against numpy-financial formulas.
Run: pytest tests/ -v
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.financial_engine import (
    FinancialProfile, months_to_debt_payoff, future_value,
    calculate_baseline, financial_health_score, project_net_worth,
)


# ── Known-answer tests ──────────────────────────────────────────

class TestDebtPayoff:
    def test_known_answer(self):
        """$18,000 @ 5.5% with $920/mo ≈ 21 months"""
        months = months_to_debt_payoff(18000, 0.055, 920)
        assert 19 <= months <= 24, f"Expected ~21 months, got {months}"

    def test_no_debt(self):
        assert months_to_debt_payoff(0, 0.055, 500) == 0

    def test_no_payment(self):
        assert months_to_debt_payoff(10000, 0.055, 0) == 9999

    def test_large_payment(self):
        """Payment > principal should return 1 month"""
        months = months_to_debt_payoff(500, 0.05, 1000)
        assert months == 1


class TestFutureValue:
    def test_lump_sum_only(self):
        """$10,000 at 7% for 10 years ≈ $19,672"""
        result = future_value(10000, 0, 0.07, 10)
        assert 19000 <= result <= 21000, f"Expected ~$19,672, got {result:.0f}"

    def test_annuity_only(self):
        """$500/mo at 7% for 10 years ≈ $86,420"""
        result = future_value(0, 500, 0.07, 10)
        assert 83000 <= result <= 90000, f"Expected ~$86,420, got {result:.0f}"

    def test_zero_years(self):
        assert future_value(5000, 100, 0.07, 0) == 5000

    def test_combined(self):
        """$12,000 lump + $500/mo at 7% for 10yr"""
        result = future_value(12000, 500, 0.07, 10)
        assert result > 90000, f"Expected >$90,000, got {result:.0f}"


class TestFinancialProfile:
    def setup_method(self):
        self.profile = FinancialProfile(
            age=28, monthly_income=6500, monthly_expenses=4200,
            total_debt=18000, debt_interest_rate=0.055,
            current_savings=12000, risk_tolerance="moderate",
        )

    def test_monthly_surplus(self):
        assert self.profile.monthly_surplus == 2300

    def test_savings_rate(self):
        rate = self.profile.savings_rate
        assert abs(rate - 2300/6500) < 0.001

    def test_net_worth(self):
        assert self.profile.net_worth == 12000 - 18000

    def test_fire_number(self):
        expected = 4200 * 12 * 25
        assert self.profile.fire_number == expected

    def test_debt_to_income(self):
        expected = 18000 / (6500 * 12)
        assert abs(self.profile.debt_to_income - expected) < 0.001


class TestCalculateBaseline:
    def test_returns_all_keys(self):
        profile = FinancialProfile(
            age=28, monthly_income=6500, monthly_expenses=4200,
            total_debt=18000, debt_interest_rate=0.055,
            current_savings=12000,
        )
        result = calculate_baseline(profile)
        required_keys = [
            "monthly_surplus", "savings_rate_pct", "net_worth",
            "debt_payoff_months", "monthly_investment", "emergency_fund_months"
        ]
        for k in required_keys:
            assert k in result, f"Missing key: {k}"

    def test_surplus_is_correct(self):
        profile = FinancialProfile(
            age=30, monthly_income=5000, monthly_expenses=3000,
            total_debt=0, debt_interest_rate=0.05, current_savings=10000,
        )
        result = calculate_baseline(profile)
        assert result["monthly_surplus"] == 2000


class TestFinancialHealthScore:
    def test_perfect_score(self):
        """High income, no debt, large savings = high score"""
        profile = FinancialProfile(
            age=35, monthly_income=10000, monthly_expenses=3000,
            total_debt=0, debt_interest_rate=0.0, current_savings=100000,
        )
        scores = financial_health_score(profile)
        assert scores["Overall"] > 70, f"Expected >70, got {scores['Overall']}"

    def test_all_dimensions_present(self):
        profile = FinancialProfile(
            age=28, monthly_income=6500, monthly_expenses=4200,
            total_debt=18000, debt_interest_rate=0.055, current_savings=12000,
        )
        scores = financial_health_score(profile)
        expected_keys = ["Savings Rate", "Emergency Fund", "Debt Load", "Investment Mix", "Cash Flow", "Overall"]
        for k in expected_keys:
            assert k in scores, f"Missing: {k}"

    def test_scores_in_range(self):
        profile = FinancialProfile(
            age=28, monthly_income=6500, monthly_expenses=4200,
            total_debt=18000, debt_interest_rate=0.055, current_savings=12000,
        )
        scores = financial_health_score(profile)
        for k, v in scores.items():
            assert 0 <= v <= 100, f"{k} out of range: {v}"


class TestProjection:
    def test_30_year_length(self):
        profile = FinancialProfile(
            age=28, monthly_income=6500, monthly_expenses=4200,
            total_debt=18000, debt_interest_rate=0.055, current_savings=12000,
        )
        projs = project_net_worth(profile, 0.065, 0.03, "balanced", 30)
        assert len(projs) == 31, f"Expected 31 entries (year 0-30), got {len(projs)}"

    def test_year_0_is_current(self):
        profile = FinancialProfile(
            age=28, monthly_income=6500, monthly_expenses=4200,
            total_debt=18000, debt_interest_rate=0.055, current_savings=12000,
        )
        projs = project_net_worth(profile, 0.065, 0.03, "balanced", 30)
        assert projs[0]["year"] == 0
        assert projs[0]["savings"] == 12000
        assert projs[0]["debt"] == 18000

    def test_net_worth_grows(self):
        profile = FinancialProfile(
            age=28, monthly_income=8000, monthly_expenses=3000,
            total_debt=0, debt_interest_rate=0.0, current_savings=10000,
        )
        projs = project_net_worth(profile, 0.07, 0.03, "invest_first", 30)
        assert projs[30]["net_worth"] > projs[0]["net_worth"], "Net worth should grow over 30 years"
