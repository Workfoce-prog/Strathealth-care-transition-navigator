from pathlib import Path
import sys

import streamlit as st

# ---------------------------------------------------------
# Project path setup
# ---------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent

if ROOT_DIR.name == "pages":
    ROOT_DIR = ROOT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ---------------------------------------------------------
# Local imports
# These files must be in the repository root:
# data.py
# ui.py
# ---------------------------------------------------------
from data import load_data
from ui import page_header


# ---------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="StratHealth AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------
@st.cache_data
def get_data():
    return load_data()


try:
    df = get_data()
except FileNotFoundError as exc:
    st.error(
        "The synthetic patient data file could not be found. "
        "Confirm that synthetic_patients.csv is in the repository root."
    )
    st.exception(exc)
    st.stop()
except KeyError as exc:
    st.error(
        "The patient dataset is missing one or more required columns. "
        "Check the column names in synthetic_patients.csv."
    )
    st.exception(exc)
    st.stop()
except Exception as exc:
    st.error("The application could not load the demonstration data.")
    st.exception(exc)
    st.stop()


# ---------------------------------------------------------
# Validate required columns
# ---------------------------------------------------------
required_columns = {
    "priority",
    "followup_scheduled",
    "risk_score",
}

missing_columns = required_columns.difference(df.columns)

if missing_columns:
    st.error(
        "The dataset is missing these required columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## StratHealth AI")
    st.caption("Care Transition Navigator")

    st.markdown("---")

    st.markdown("### Demonstration status")
    st.success("Synthetic data only")

    st.markdown("### Intended purpose")
    st.write(
        "Demonstrate explainable patient prioritization and post-discharge "
        "care-coordination workflows."
    )

    st.markdown("### Not intended for")
    st.write(
        "Diagnosis, treatment selection, medication changes, or autonomous "
        "clinical decision-making."
    )

    st.markdown("---")

    st.caption(
        "A demonstration product of StratDesign Solutions — "
        "AI & Analytics Solutions."
    )


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
page_header(
    "StratHealth AI — Care Transition Navigator",
    "Explainable post-discharge risk and follow-up prioritization demonstration",
)


# ---------------------------------------------------------
# Introductory banner
# ---------------------------------------------------------
st.info(
    "This prototype uses synthetic patient records and illustrative risk "
    "thresholds. It is designed to demonstrate workflow concepts and is not "
    "connected to an electronic health record."
)


# ---------------------------------------------------------
# Key metrics
# ---------------------------------------------------------
high_critical_count = int(
    df["priority"].isin(["High", "Critical"]).sum()
)

no_followup_count = int(
    df["followup_scheduled"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("no")
    .sum()
)

average_risk = float(df["risk_score"].mean())

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    label="Synthetic patients",
    value=f"{len(df):,}",
)

c2.metric(
    label="High or critical",
    value=f"{high_critical_count:,}",
)

c3.metric(
    label="No follow-up scheduled",
    value=f"{no_followup_count:,}",
)

c4.metric(
    label="Average modeled risk",
    value=f"{average_risk:.1f}/100",
)


st.markdown("---")


# ---------------------------------------------------------
# Main content
# ---------------------------------------------------------
left_col, right_col = st.columns([1.4, 1])

with left_col:
    st.markdown("### What this prototype demonstrates")

    st.write(
        "The Care Transition Navigator helps care teams identify which "
        "recently discharged patients may benefit from earlier review. "
        "It also shows the main factors contributing to a patient's priority "
        "score and allows users to test illustrative care-coordination scenarios."
    )

    st.markdown("### Core capabilities")

    st.markdown(
        """
        - Prioritize recently discharged patients for follow-up
        - Classify patients into routine, moderate, high, and critical groups
        - Display the major factors contributing to modeled risk
        - Identify patients without scheduled follow-up
        - Support care-coordination workflow planning
        - Demonstrate responsible and explainable AI controls
        """
    )

    st.markdown("### Navigate the demonstration")

    st.write(
        "Use the pages in the left sidebar to review the executive dashboard, "
        "patient priority worklist, individual risk profile, intervention "
        "simulator, model performance, and AI governance documentation."
    )

with right_col:
    st.markdown("### Intended users")

    st.markdown(
        """
        - Care coordinators
        - Transitional-care nurses
        - Quality-improvement teams
        - Population-health teams
        - Clinical operations leaders
        - Healthcare analytics teams
        """
    )

    st.markdown("### Illustrative workflow")

    st.markdown(
        """
        1. Review the prioritized patient worklist  
        2. Open a patient's risk profile  
        3. Examine the leading modeled risk factors  
        4. Review follow-up and care-coordination needs  
        5. Test illustrative intervention scenarios  
        6. Document clinician or care-team review  
        """
    )


st.markdown("---")


# ---------------------------------------------------------
# Priority summary
# ---------------------------------------------------------
st.markdown("### Patient priority overview")

priority_order = ["Routine", "Moderate", "High", "Critical"]

priority_summary = (
    df["priority"]
    .value_counts()
    .reindex(priority_order, fill_value=0)
    .rename_axis("Priority")
    .reset_index(name="Patients")
)

st.dataframe(
    priority_summary,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Limitations
# ---------------------------------------------------------
st.markdown("### Important limitations")

st.warning(
    """
    This application is a demonstration only.

    - It is not connected to an electronic health record.
    - It has not been clinically validated.
    - All patient records are synthetic.
    - Risk probabilities and thresholds are illustrative.
    - Suggested workflows are operational examples, not treatment recommendations.
    - A qualified clinician or care professional must make all final decisions.
    """
)


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")

st.caption(
    "StratHealth AI Care Transition Navigator | "
    "StratDesign Solutions — AI & Analytics Solutions | "
    "Synthetic demonstration data only"
)
