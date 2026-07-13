from pathlib import Path
import sys

# Ensure the repository root is importable on Streamlit Cloud and local runs.
ROOT_DIR = Path(__file__).resolve().parent
if ROOT_DIR.name == "pages":
    ROOT_DIR = ROOT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import plotly.express as px
import streamlit as st
from utils.data import load_data
from utils.ui import page_header

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")
df = load_data()
page_header("Executive Dashboard", "Current synthetic discharge cohort")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Patients", len(df))
c2.metric("Critical", int((df.priority == "Critical").sum()))
c3.metric("High", int((df.priority == "High").sum()))
c4.metric("Transportation barriers", int((df.transportation_barrier == "Yes").sum()))
c5.metric("Medication review flags", int((df.medication_count >= 10).sum()))

left, right = st.columns(2)
with left:
    counts = df["priority"].value_counts().reindex(["Routine", "Moderate", "High", "Critical"]).reset_index()
    counts.columns = ["Priority", "Patients"]
    st.plotly_chart(px.bar(counts, x="Priority", y="Patients", title="Patients by priority band"), use_container_width=True)
with right:
    cond = df.groupby("primary_condition", as_index=False)["risk_score"].mean().sort_values("risk_score", ascending=False)
    st.plotly_chart(px.bar(cond, x="primary_condition", y="risk_score", title="Average risk by primary condition"), use_container_width=True)

st.markdown("### Operational indicators")
ops = {
    "Follow-up not scheduled": (df.followup_scheduled == "No").sum(),
    "Lives alone": (df.lives_alone == "Yes").sum(),
    "No home-health referral": (df.home_health_referral == "No").sum(),
    "30+ miles from care": (df.rural_distance_miles >= 30).sum(),
}
st.dataframe(
    [{"Indicator": k, "Patients": int(v), "Share": f"{v/len(df):.1%}"} for k, v in ops.items()],
    use_container_width=True,
    hide_index=True,
)
