from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_WEIGHTS = {
    "age": 0.08,
    "chronic_conditions": 0.13,
    "prior_admissions_12m": 0.16,
    "prior_ed_visits_12m": 0.11,
    "length_of_stay": 0.07,
    "medication_count": 0.09,
    "no_followup_scheduled": 0.12,
    "transportation_barrier": 0.07,
    "lives_alone": 0.05,
    "rural_distance_miles": 0.05,
    "home_health_not_referred": 0.04,
    "high_risk_condition": 0.03,
}


def _minmax(series: pd.Series, lower: float, upper: float) -> pd.Series:
    return ((series.clip(lower, upper) - lower) / (upper - lower)).fillna(0)


def score_patients(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    components = pd.DataFrame(index=out.index)
    components["age"] = _minmax(out["age"], 40, 95)
    components["chronic_conditions"] = _minmax(out["chronic_conditions"], 0, 8)
    components["prior_admissions_12m"] = _minmax(out["prior_admissions_12m"], 0, 5)
    components["prior_ed_visits_12m"] = _minmax(out["prior_ed_visits_12m"], 0, 8)
    components["length_of_stay"] = _minmax(out["length_of_stay"], 1, 20)
    components["medication_count"] = _minmax(out["medication_count"], 0, 20)
    components["no_followup_scheduled"] = (out["followup_scheduled"] == "No").astype(float)
    components["transportation_barrier"] = (out["transportation_barrier"] == "Yes").astype(float)
    components["lives_alone"] = (out["lives_alone"] == "Yes").astype(float)
    components["rural_distance_miles"] = _minmax(out["rural_distance_miles"], 0, 60)
    components["home_health_not_referred"] = (out["home_health_referral"] == "No").astype(float)
    components["high_risk_condition"] = out["primary_condition"].isin(["Heart Failure", "COPD", "Diabetes"]).astype(float)

    weighted = sum(components[c] * w for c, w in FEATURE_WEIGHTS.items())
    out["risk_score"] = np.round((weighted / sum(FEATURE_WEIGHTS.values())) * 125).clip(0, 100).astype(int)
    out["readmission_probability"] = np.round(0.06 + 0.0042 * out["risk_score"], 3).clip(0.05, 0.55)
    out["priority"] = pd.cut(
        out["risk_score"],
        bins=[-1, 39, 59, 79, 100],
        labels=["Routine", "Moderate", "High", "Critical"],
    ).astype(str)
    return out


def top_drivers(row: pd.Series, max_drivers: int = 5) -> list[str]:
    drivers: list[tuple[str, float]] = []
    mapping = {
        "Older age": max((row["age"] - 40) / 55, 0) * FEATURE_WEIGHTS["age"],
        "Multiple chronic conditions": min(row["chronic_conditions"] / 8, 1) * FEATURE_WEIGHTS["chronic_conditions"],
        "Prior hospital admissions": min(row["prior_admissions_12m"] / 5, 1) * FEATURE_WEIGHTS["prior_admissions_12m"],
        "Prior emergency visits": min(row["prior_ed_visits_12m"] / 8, 1) * FEATURE_WEIGHTS["prior_ed_visits_12m"],
        "Longer hospital stay": min(max(row["length_of_stay"] - 1, 0) / 19, 1) * FEATURE_WEIGHTS["length_of_stay"],
        "High medication burden": min(row["medication_count"] / 20, 1) * FEATURE_WEIGHTS["medication_count"],
        "No follow-up scheduled": (row["followup_scheduled"] == "No") * FEATURE_WEIGHTS["no_followup_scheduled"],
        "Transportation barrier": (row["transportation_barrier"] == "Yes") * FEATURE_WEIGHTS["transportation_barrier"],
        "Lives alone": (row["lives_alone"] == "Yes") * FEATURE_WEIGHTS["lives_alone"],
        "Rural travel distance": min(row["rural_distance_miles"] / 60, 1) * FEATURE_WEIGHTS["rural_distance_miles"],
        "No home-health referral": (row["home_health_referral"] == "No") * FEATURE_WEIGHTS["home_health_not_referred"],
        "Higher-risk condition group": (row["primary_condition"] in ["Heart Failure", "COPD", "Diabetes"]) * FEATURE_WEIGHTS["high_risk_condition"],
    }
    drivers.extend(mapping.items())
    return [name for name, value in sorted(drivers, key=lambda x: x[1], reverse=True) if value > 0][:max_drivers]


def workflow_action(priority: str) -> str:
    return {
        "Routine": "Standard discharge workflow",
        "Moderate": "Confirm follow-up within 7 days",
        "High": "Care coordinator review within 48 hours",
        "Critical": "Clinical-team review within 24 hours",
    }[priority]
