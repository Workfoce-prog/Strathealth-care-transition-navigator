from pathlib import Path
import sys

# Ensure the repository root is importable on Streamlit Cloud and local runs.
ROOT_DIR = Path(__file__).resolve().parent
if ROOT_DIR.name == "pages":
    ROOT_DIR = ROOT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from utils.data import load_data
from utils.ui import page_header

st.set_page_config(page_title="StratHealth AI", page_icon="🏥", layout="wide")
df = load_data()

page_header(
    "StratHealth AI — Care Transition Navigator",
    "Explainable post-discharge risk and follow-up prioritization demonstration",
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Synthetic patients", f"{len(df):,}")
c2.metric("High or critical", f"{df['priority'].isin(['High','Critical']).sum():,}")
c3.metric("No follow-up scheduled", f"{(df['followup_scheduled']=='No').sum():,}")
c4.metric("Average modeled risk", f"{df['risk_score'].mean():.1f}/100")

st.markdown("### What this prototype demonstrates")
st.write(
    "The navigator helps care teams identify which recently discharged patients may benefit from earlier review, "
    "understand the main contributors to the priority score, and test illustrative care-coordination scenarios."
)

st.markdown("### Navigate the demo")
st.write(
    "Use the pages in the left sidebar to review the executive dashboard, prioritized worklist, patient risk profile, "
    "scenario simulator, model performance, and AI governance documentation."
)

st.markdown("### Intended users")
st.write("Care coordinators, transitional-care nurses, quality-improvement teams, population-health teams, and clinical leaders.")

st.markdown("### Important limitation")
st.warning(
    "This prototype is not connected to an electronic health record and has not been clinically validated. "
    "All thresholds, probabilities, records, and intervention effects are illustrative."
)
