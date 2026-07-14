import re
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "synthetic_patients.csv"


REQUIRED_COLUMNS = [
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


COLUMN_ALIASES = {
    # Patient identifier
    "patient": "patient_id",
    "patient_number": "patient_id",
    "member_id": "patient_id",
    "person_id": "patient_id",
    "id": "patient_id",

    # Demographics
    "gender": "sex",
    "patient_age": "age",
    "age_years": "age",

    # Conditions
    "number_chronic_conditions": "chronic_conditions",
    "num_chronic_conditions": "chronic_conditions",
    "chronic_condition_count": "chronic_conditions",
    "condition_count": "chronic_conditions",

    # Prior utilization
    "previous_admissions": "prior_admissions",
    "past_admissions": "prior_admissions",
    "admissions_last_year": "prior_admissions",
    "prior_hospitalizations": "prior_admissions",

    "previous_ed_visits": "prior_ed_visits",
    "emergency_visits": "prior_ed_visits",
    "ed_visits": "prior_ed_visits",
    "ed_visits_last_year": "prior_ed_visits",

    # Current encounter
    "los": "length_of_stay",
    "hospital_length_of_stay": "length_of_stay",
    "days_in_hospital": "length_of_stay",

    # Medications
    "number_medications": "medication_count",
    "num_medications": "medication_count",
    "medications": "medication_count",
    "medication_total": "medication_count",

    # Follow-up
    "follow_up_scheduled": "followup_scheduled",
    "followup": "followup_scheduled",
    "follow_up": "followup_scheduled",
    "appointment_scheduled": "followup_scheduled",

    # Primary care
    "primary_care_connection": "primary_care_connected",
    "pcp_connected": "primary_care_connected",
    "has_primary_care": "primary_care_connected",
    "primary_care_provider": "primary_care_connected",

    # Social-needs indicators
    "transport_barrier": "transportation_barrier",
    "transportation_issue": "transportation_barrier",
    "transportation_need": "transportation_barrier",

    "living_alone": "lives_alone",
    "patient_lives_alone": "lives_alone",
}


DEFAULT_VALUES = {
    "patient_id": None,
    "age": 65,
    "sex": "Unknown",
    "chronic_conditions": 0,
    "prior_admissions": 0,
    "prior_ed_visits": 0,
    "length_of_stay": 1,
    "medication_count": 0,
    "followup_scheduled": "No",
    "primary_care_connected": "No",
    "transportation_barrier": "No",
    "lives_alone": "No",
}


def normalize_column_name(column_name: str) -> str:
    """
    Convert column names to lowercase snake_case.
    """

    name = str(column_name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name)

    return name.strip("_")


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize CSV column names and apply known aliases.
    """

    standardized = df.copy()

    standardized.columns = [
        normalize_column_name(column)
        for column in standardized.columns
    ]

    rename_map = {
        column: COLUMN_ALIASES[column]
        for column in standardized.columns
        if column in COLUMN_ALIASES
    }

    standardized = standardized.rename(columns=rename_map)

    # Remove duplicated columns that may result from aliases.
    standardized = standardized.loc[
        :,
        ~standardized.columns.duplicated()
    ]

    return standardized


def add_missing_demo_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add missing fields using safe synthetic demonstration defaults.
    """

    completed = df.copy()

    for column, default_value in DEFAULT_VALUES.items():
        if column not in completed.columns:
            if column == "patient_id":
                completed[column] = [
                    f"DEMO-{number:04d}"
                    for number in range(1, len(completed) + 1)
                ]
            else:
                completed[column] = default_value

    return completed


def normalize_yes_no(value) -> str:
    """
    Standardize common boolean values as Yes or No.
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
        "positive",
    }

    return "Yes" if normalized in yes_values else "No"


def clean_source_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean numeric, categorical, and Yes/No fields.
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
        ).fillna(DEFAULT_VALUES[column])

    cleaned["age"] = cleaned["age"].clip(0, 110)

    for column in [
        "chronic_conditions",
        "prior_admissions",
        "prior_ed_visits",
        "length_of_stay",
        "medication_count",
    ]:
        cleaned[column] = cleaned[column].clip(lower=0)

    yes_no_columns = [
        "followup_scheduled",
        "primary_care_connected",
        "transportation_barrier",
        "lives_alone",
    ]

    for column in yes_no_columns:
        cleaned[column] = cleaned[column].apply(normalize_yes_no)

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


def validate_source_data(df: pd.DataFrame) -> None:
    """
    Confirm that the standardized demonstration dataset is usable.
    """

    if df.empty:
        raise ValueError(
            "The synthetic patient dataset contains no records."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            "Required columns are still missing after standardization: "
            + ", ".join(missing_columns)
        )


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load, standardize, clean, and score synthetic patient data.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cannot find the data file: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        raise ValueError(
            "synthetic_patients.csv contains no patient records."
        )

    # Fix inconsistent column names.
    df = standardize_columns(df)

    # Add any fields absent from the original demonstration CSV.
    df = add_missing_demo_columns(df)

    # Validate after standardization and default creation.
    validate_source_data(df)

    # Clean all values.
    df = clean_source_data(df)

    # Use your existing scoring function.
    df = score_patients(df)

    # Add explanations and suggested workflows.
    df["top_drivers"] = df.apply(top_drivers, axis=1)
    df["workflow_action"] = df.apply(
        workflow_action,
        axis=1,
    )

    return df
