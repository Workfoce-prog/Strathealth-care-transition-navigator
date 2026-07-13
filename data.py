from __future__ import annotations

from pathlib import Path
import pandas as pd
from utils.scoring import score_patients, top_drivers, workflow_action

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_patients.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = score_patients(df)
    df["top_drivers"] = df.apply(lambda r: "; ".join(top_drivers(r)), axis=1)
    df["suggested_workflow"] = df["priority"].map(workflow_action)
    return df
