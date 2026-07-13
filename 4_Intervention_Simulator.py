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
from utils.scoring import score_patients
from utils.ui import page_header

st.set_page_config(page_title="Scenario Simulator", page_icon="🧪", layout="wide")
df = load_data().sort_values("risk_score", ascending=False)
page_header("Illustrative Intervention Simulator", "Explore how modifiable workflow factors influence the demonstration score")

patient_id = st.selectbox("Select patient", df.patient_id.tolist())
base = df.loc[df.patient_id == patient_id].iloc[0]
scenario = base.copy()

st.markdown("### Select illustrative supports")
c1, c2 = st.columns(2)
followup = c1.checkbox("Schedule follow-up within 7 days", value=base.followup_scheduled == "Yes")
transport = c1.checkbox("Transportation support arranged", value=base.transportation_barrier == "No")
home_health = c2.checkbox("Home-health/care-coordination referral completed", value=base.home_health_referral == "Yes")
med_recon = c2.checkbox("Medication reconciliation completed", value=False)

scenario["followup_scheduled"] = "Yes" if followup else "No"
scenario["transportation_barrier"] = "No" if transport else "Yes"
scenario["home_health_referral"] = "Yes" if home_health else "No"
if med_recon:
    scenario["medication_count"] = max(int(base.medication_count) - 2, 0)

new = score_patients(scenario.to_frame().T).iloc[0]

m1, m2, m3 = st.columns(3)
m1.metric("Baseline score", int(base.risk_score))
m2.metric("Scenario score", int(new.risk_score), delta=int(new.risk_score - base.risk_score))
m3.metric("Scenario priority", new.priority)

st.warning("Scenario changes are illustrative. They do not estimate causal treatment effects or guarantee improved outcomes.")
