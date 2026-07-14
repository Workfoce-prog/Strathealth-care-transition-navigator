from pathlib import Path
from typing import List

import pandas as pd

from scoring import score_patients, top_drivers, workflow_action


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "synthetic_patients.csv"


# ---------------------------------------------------------
# Expected source columns
# ---------------------------------------------------------
EXPECTED_COLUMNS: List[str] = [
    "patient_id",
    "age",
    "sex",
    "chronic_conditions",
    "prior_admissions",
    "prior_ed_visits",
    "length_of_stay",
    "medication_count",
    "followup_scheduled",
    "primary_care_connected",
    "transportation_barrier",
    "lives_alone",
]


# ---------------------------------------------------------
# Normalize Yes/No variables
# ---------------------------------------------------------
def normalize_yes_no(value) -> str:
    """
    Convert common boolean and Yes/No representations to
    standardized values of 'Yes' or 'No'.
    """

    if pd.isna(value):
        return "No"

    normalized = str(value).strip().lower()

    yes_values = {
        "yes",
        "y",
        "true",
        "1",
        "1.0",
    }

    return "Yes" if normalized in yes_values else "No"


# ---------------------------------------------------------
# Normalize priority values
# ---------------------------------------------------------
def normalize_priority(value) -> str:
    """
    Standardize patient priority labels.
    """

    if pd.isna(value):
        return "Routine"

    normalized = str(value).strip().lower()

    priority_map = {
        "routine": "Routine",
        "low": "Routine",
        "moderate": "Moderate",
        "medium": "Moderate",
        "high": "High",
        "critical": "Critical",
        "severe": "Critical",
    }

    return priority_map.get(normalized, "Routine")


# ---------------------------------------------------------
# Validate source dataset
# ---------------------------------------------------------
def validate_source_data(df: pd.DataFrame) -> None:
    """
    Validate that the synthetic patient dataset contains
    the minimum columns required by the scoring functions.
    """

    if df.empty:
        raise ValueError(
            "The synthetic patient dataset is empty."
        )

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            "The synthetic patient dataset is missing required columns: "
            + ", ".join(missing_columns)
        )


# ---------------------------------------------------------
# Clean source dataset
# ---------------------------------------------------------
def clean_source_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the synthetic patient dataset.
    """

    cleaned = df.copy()

    numeric_columns = [
        "age",
        "chronic_conditions",
        "prior_admissions",
        "prior_ed_visits",
        "length_of_stay",
        "medication_count",
    ]

    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce",
        ).fillna(0)

    cleaned["age"] = cleaned["age"].clip(lower=0, upper=110)

    nonnegative_columns = [
        "chronic_conditions",
        "prior_admissions",
        "prior_ed_visits",
        "length_of_stay",
        "medication_count",
    ]

    for column in nonnegative_columns:
        cleaned[column] = cleaned[column].clip(lower=0)

    yes_no_columns = [
        "followup_scheduled",
        "primary_care_connected",
        "transportation_barrier",
        "lives_alone",
    ]

    for column in yes_no_columns:
        cleaned[column] = cleaned[column].apply(
            normalize_yes_no
        )

    cleaned["patient_id"] = (
        cleaned["patient_id"]
        .astype(str)
        .str.strip()
    )

    cleaned["sex"] = (
        cleaned["sex"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    return cleaned


# ---------------------------------------------------------
# Load and score patient data
# ---------------------------------------------------------
def load_data() -> pd.DataFrame:
    """
    Load synthetic patient records, clean the data, calculate
    modeled risk scores, assign priority groups, identify leading
    risk drivers, and generate illustrative workflow actions.

    Returns
    -------
    pandas.DataFrame
        Scored synthetic patient data.

    Raises
    ------
    FileNotFoundError
        If synthetic_patients.csv is not found.

    ValueError
        If the dataset is empty or scoring returns an invalid result.

    KeyError
        If required columns are missing.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "The synthetic patient dataset could not be found.\n\n"
            f"Expected location: {DATA_FILE}\n\n"
            "Confirm that synthetic_patients.csv is uploaded to "
            "the same GitHub directory as app.py and data.py."
        )

    try:
        df = pd.read_csv(DATA_FILE)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            "synthetic_patients.csv exists, but it contains no data."
        ) from exc
    except pd.errors.ParserError as exc:
        raise ValueError(
            "synthetic_patients.csv could not be parsed. "
            "Check the CSV formatting."
        ) from exc

    validate_source_data(df)

    df = clean_source_data(df)

    # score_patients must return a DataFrame containing:
    # risk_score and priority
    scored_df = score_patients(df)

    if scored_df is None:
        raise ValueError(
            "score_patients returned no result."
        )

    if not isinstance(scored_df, pd.DataFrame):
        raise TypeError(
            "score_patients must return a pandas DataFrame."
        )

    required_scored_columns = {
        "risk_score",
        "priority",
    }

    missing_scored_columns = (
        required_scored_columns.difference(scored_df.columns)
    )

    if missing_scored_columns:
        raise KeyError(
            "The scoring function did not create these required columns: "
            + ", ".join(sorted(missing_scored_columns))
        )

    scored_df["risk_score"] = pd.to_numeric(
        scored_df["risk_score"],
        errors="coerce",
    ).fillna(0)

    scored_df["risk_score"] = scored_df["risk_score"].clip(
        lower=0,
        upper=100,
    )

    scored_df["priority"] = scored_df["priority"].apply(
        normalize_priority
    )

    # Add explainability fields.
    scored_df["top_drivers"] = scored_df.apply(
        top_drivers,
        axis=1,
    )

    # Add illustrative care-coordination workflow.
    scored_df["workflow_action"] = scored_df.apply(
        workflow_action,
        axis=1,
    )

    priority_order = {
        "Critical": 1,
        "High": 2,
        "Moderate": 3,
        "Routine": 4,
    }

    scored_df["_priority_order"] = (
        scored_df["priority"]
        .map(priority_order)
        .fillna(5)
    )

    scored_df = (
        scored_df
        .sort_values(
            by=["_priority_order", "risk_score"],
            ascending=[True, False],
        )
        .drop(columns=["_priority_order"])
        .reset_index(drop=True)
    )

    return scored_df


# ---------------------------------------------------------
# Optional summary function
# ---------------------------------------------------------
def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Return summary statistics used by the Streamlit dashboard.
    """

    required_columns = {
        "priority",
        "followup_scheduled",
        "risk_score",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise KeyError(
            "Cannot create the dashboard summary because these "
            "columns are missing: "
            + ", ".join(sorted(missing_columns))
        )

    high_or_critical = int(
        df["priority"].isin(["High", "Critical"]).sum()
    )

    no_followup = int(
        df["followup_scheduled"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("no")
        .sum()
    )

    return {
        "total_patients": int(len(df)),
        "high_or_critical": high_or_critical,
        "no_followup": no_followup,
        "average_risk": float(df["risk_score"].mean()),
    }


# ---------------------------------------------------------
# Local testing
# ---------------------------------------------------------
if __name__ == "__main__":
    try:
        patient_data = load_data()

        print("Synthetic patient data loaded successfully.")
        print(f"Number of patients: {len(patient_data):,}")
        print("\nAvailable columns:")
        print(patient_data.columns.tolist())

        print("\nPriority distribution:")
        print(patient_data["priority"].value_counts())

        print("\nDashboard summary:")
        print(get_data_summary(patient_data))

    except Exception as error:
        print(f"Data loading failed: {error}")
        raise
