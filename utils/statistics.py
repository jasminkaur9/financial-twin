"""
Statistical Analysis — Multi-model divergence significance testing.

Pearson/Spearman correlations, p-values, and rolling correlation
across the three AI model net-worth projections.

Used in synthesize_council() and displayed in the Divergence tab.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple


# ── Correlation helpers ───────────────────────────────────────────────────────

def pearson_correlation(a: List[float], b: List[float]) -> Tuple[float, float]:
    """
    Pearson r between two series.
    Returns (r, p_value).
    """
    r, p = stats.pearsonr(a, b)
    return round(float(r), 4), round(float(p), 6)


def spearman_correlation(a: List[float], b: List[float]) -> Tuple[float, float]:
    """
    Spearman rho between two series.
    Returns (rho, p_value).
    """
    rho, p = stats.spearmanr(a, b)
    return round(float(rho), 4), round(float(p), 6)


def rolling_correlation(
    a: List[float], b: List[float], window: int = 5
) -> List[Optional[float]]:
    """
    Year-by-year rolling Pearson r with a given window.
    Returns None for the first (window - 1) entries.
    """
    result: List[Optional[float]] = []
    for i in range(len(a)):
        if i < window - 1:
            result.append(None)
        else:
            r, _ = stats.pearsonr(a[i - window + 1 : i + 1], b[i - window + 1 : i + 1])
            result.append(round(float(r), 4))
    return result


# ── Annual growth rate helpers ────────────────────────────────────────────────

def annual_growth_rates(net_worth_series: List[float]) -> List[Optional[float]]:
    """
    Year-over-year growth rate from a net worth series.
    Returns None for year 0 (no prior year).
    Skips division where prior value is 0 or negative.
    """
    rates: List[Optional[float]] = [None]
    for i in range(1, len(net_worth_series)):
        prev = net_worth_series[i - 1]
        if prev > 0:
            rates.append(round((net_worth_series[i] - prev) / prev, 6))
        else:
            rates.append(None)
    return rates


# ── Main divergence statistics ────────────────────────────────────────────────

def model_divergence_stats(council_results: dict) -> Dict:
    """
    Full statistical analysis across all 3 model projections.

    Computes:
    - Pairwise Pearson r + p-value (level trajectories)
    - Pairwise Spearman rho + p-value (level trajectories)
    - Rolling 5-year Pearson r (GPT vs Gemini — the widest gap)
    - Net worth spread at years 10, 20, 30 with CV and std
    - Annual growth rate correlation (more meaningful than level correlation)
    """
    # Extract net worth levels per model
    levels: Dict[str, List[float]] = {}
    for key, analysis in council_results.items():
        levels[key] = [p.net_worth for p in analysis.projections]

    model_keys = list(levels.keys())

    # ── Pairwise stats on levels ──────────────────────────────────────────────
    pairs = [
        (model_keys[i], model_keys[j])
        for i in range(len(model_keys))
        for j in range(i + 1, len(model_keys))
    ]

    pairwise: Dict[str, dict] = {}
    for ak, bk in pairs:
        r, p_r = pearson_correlation(levels[ak], levels[bk])
        rho, p_rho = spearman_correlation(levels[ak], levels[bk])
        label = f"{ak}_vs_{bk}"
        pairwise[label] = {
            "pearson_r": r,
            "pearson_p": p_r,
            "pearson_significant": p_r < 0.05,
            "spearman_rho": rho,
            "spearman_p": p_rho,
            "spearman_significant": p_rho < 0.05,
        }

    # ── Annual growth-rate correlation (removes compounding trend) ────────────
    growth_rates: Dict[str, List[float]] = {}
    for key, series in levels.items():
        rates = annual_growth_rates(series)
        # Drop the None at index 0
        growth_rates[key] = [r for r in rates if r is not None]

    growth_pairwise: Dict[str, dict] = {}
    for ak, bk in pairs:
        if ak in growth_rates and bk in growth_rates:
            gr, gp_r = pearson_correlation(growth_rates[ak], growth_rates[bk])
            grho, gp_rho = spearman_correlation(growth_rates[ak], growth_rates[bk])
            label = f"{ak}_vs_{bk}"
            growth_pairwise[label] = {
                "pearson_r": gr,
                "pearson_p": gp_r,
                "pearson_significant": gp_r < 0.05,
                "spearman_rho": grho,
                "spearman_p": gp_rho,
                "spearman_significant": gp_rho < 0.05,
            }

    # ── Rolling correlation: most divergent pair (GPT vs Gemini) ─────────────
    rolling: List[Optional[float]] = []
    if "gpt" in levels and "gemini" in levels:
        rolling = rolling_correlation(levels["gpt"], levels["gemini"], window=5)

    # ── Spread statistics at key years ────────────────────────────────────────
    nw_by_year: Dict[str, dict] = {}
    for year in [10, 20, 30]:
        vals = {k: s[year] for k, s in levels.items() if len(s) > year}
        if vals:
            v_list = list(vals.values())
            mean_v = float(np.mean(v_list))
            std_v = float(np.std(v_list))
            nw_by_year[f"year_{year}"] = {
                "values": {k: round(v, 0) for k, v in vals.items()},
                "mean": round(mean_v, 0),
                "std": round(std_v, 0),
                "cv_pct": round(std_v / abs(mean_v) * 100, 1) if mean_v != 0 else 0.0,
                "spread": round(max(v_list) - min(v_list), 0),
            }

    # ── Paired t-tests: is each model pair's trajectory significantly different? ──
    # Paired t-test is appropriate here: for each year, we compare model A vs model B.
    # A significant result means model A's trajectory is systematically higher/lower.
    paired_ttests: Dict = {}
    for ak, bk in pairs:
        a_series = levels[ak]
        b_series = levels[bk]
        t_stat, p_t = stats.ttest_rel(a_series, b_series)
        label = f"{ak}_vs_{bk}"
        paired_ttests[label] = {
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_t), 6),
            "significant": float(p_t) < 0.05,
            "interpretation": (
                f"{ak.upper()} trajectory is statistically significantly different "
                f"from {bk.upper()} (paired t-test, p < 0.05)"
                if float(p_t) < 0.05
                else f"No significant difference between {ak.upper()} and {bk.upper()} trajectories"
            ),
        }
    anova_result = paired_ttests  # kept as "anova" key for backwards compatibility

    return {
        "pairwise_correlations": pairwise,
        "growth_rate_correlations": growth_pairwise,
        "rolling_correlation_gpt_gemini": rolling,
        "net_worth_by_year": nw_by_year,
        "anova": anova_result,
        "summary": _build_summary(pairwise, growth_pairwise, nw_by_year, anova_result),
    }


def _build_summary(
    pairwise: Dict,
    growth_pairwise: Dict,
    nw_by_year: Dict,
    paired_ttests: Dict,
) -> str:
    parts = []

    for label, s in pairwise.items():
        a, b = label.split("_vs_")
        sig = "p<0.05 ✓" if s["pearson_significant"] else "n.s."
        parts.append(f"{a.upper()} vs {b.upper()}: r={s['pearson_r']}, ρ={s['spearman_rho']} ({sig})")

    if "year_30" in nw_by_year:
        y30 = nw_by_year["year_30"]
        parts.append(f"Year-30 spread=${y30['spread']:,.0f}, CV={y30['cv_pct']}%")

    for label, t in paired_ttests.items():
        if t["significant"]:
            a, b = label.split("_vs_")
            parts.append(f"Paired t-test {a.upper()} vs {b.upper()}: p={t['p_value']} (significant)")

    return " | ".join(parts)
