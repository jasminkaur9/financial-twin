"""
Data Fetcher — Real economic indicators from FRED.
Falls back to hardcoded sensible defaults if API is unavailable.
"""

import os
from datetime import datetime
from typing import Dict


FRED_DEFAULTS = {
    "inflation_rate": 3.1,       # CPI YoY %
    "treasury_10y": 4.5,         # 10-Year Treasury yield %
    "fed_funds_rate": 5.25,      # Federal funds rate %
    "savings_rate": 4.75,        # High-yield savings APY %
    "source": "defaults",
    "note": "Set FRED_API_KEY in .env for live data",
}


def get_fred_rates() -> Dict:
    """
    Fetch live economic rates from FRED API.
    Series used:
      CPIAUCSL — CPI (inflation)
      DGS10    — 10-Year Treasury yield
      DFF      — Federal funds rate
    """
    api_key = os.getenv("FRED_API_KEY", "")
    if not api_key:
        return {**FRED_DEFAULTS, "timestamp": datetime.now().isoformat()}

    try:
        from fredapi import Fred
        fred = Fred(api_key=api_key)

        # CPI YoY inflation
        cpi = fred.get_series("CPIAUCSL")
        inflation = float(cpi.pct_change(12).dropna().iloc[-1] * 100)

        # 10Y Treasury
        t10 = fred.get_series("DGS10")
        treasury = float(t10.dropna().iloc[-1])

        # Fed Funds
        dff = fred.get_series("DFF")
        fed_funds = float(dff.dropna().iloc[-1])

        return {
            "inflation_rate": round(inflation, 2),
            "treasury_10y": round(treasury, 2),
            "fed_funds_rate": round(fed_funds, 2),
            "savings_rate": round(fed_funds * 0.95, 2),  # HYSA ≈ 95% of fed funds
            "source": "FRED",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            **FRED_DEFAULTS,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


def validate_model_assumptions(fred_data: Dict, model_assumptions: Dict) -> Dict:
    """
    Compare AI model economic assumptions against FRED ground truth.
    Returns validation report for audit trail.
    """
    actual_inflation = fred_data.get("inflation_rate", FRED_DEFAULTS["inflation_rate"])
    actual_treasury = fred_data.get("treasury_10y", FRED_DEFAULTS["treasury_10y"])

    report = {}
    for model_name, assumptions in model_assumptions.items():
        model_inflation = assumptions.get("inflation", 0) * 100
        model_return = assumptions.get("return", 0) * 100

        report[model_name] = {
            "inflation_assumed": f"{model_inflation:.1f}%",
            "inflation_actual_fred": f"{actual_inflation:.1f}%",
            "inflation_delta": f"{model_inflation - actual_inflation:+.1f}%",
            "return_assumed": f"{model_return:.1f}%",
            "treasury_10y_fred": f"{actual_treasury:.1f}%",
            "equity_risk_premium_implied": f"{model_return - actual_treasury:.1f}%",
        }
    return report
