from __future__ import annotations
from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).with_name("care_transition_model.pkl")
FEATURES = ["age","sex","primary_condition","chronic_conditions","prior_admissions_12m","prior_ed_visits_12m","length_of_stay","medication_count","followup_scheduled","transportation_barrier","lives_alone","rural_distance_miles","home_health_referral"]

def load_model():
    return joblib.load(MODEL_PATH)

def predict_probabilities(df: pd.DataFrame) -> pd.Series:
    missing=[c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    model=load_model()
    return pd.Series(model.predict_proba(df[FEATURES])[:,1],index=df.index,name="readmission_probability")

def priority_from_probability(p: float) -> str:
    if p >= .70: return "Critical"
    if p >= .50: return "High"
    if p >= .30: return "Moderate"
    return "Routine"
