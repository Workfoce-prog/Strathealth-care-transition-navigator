import plotly.express as px
import streamlit as st
from utils.data import load_data
from utils.scoring import top_drivers
from utils.ui import page_header

st.set_page_config(page_title="Patient Risk Profile", page_icon="🧭", layout="wide")
df = load_data().sort_values("risk_score", ascending=False)
page_header("Patient Risk Profile", "Explainable review of one synthetic patient")

patient_id = st.selectbox("Select patient", df.patient_id.tolist())
r = df.loc[df.patient_id == patient_id].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Risk score", f"{r.risk_score}/100")
c2.metric("Priority", r.priority)
c3.metric("Modeled readmission risk", f"{r.readmission_probability:.1%}")
c4.metric("Follow-up scheduled", r.followup_scheduled)

left, right = st.columns([1, 1])
with left:
    st.markdown("### Patient context")
    st.dataframe({
        "Attribute": ["Age", "Primary condition", "Chronic conditions", "Prior admissions", "Prior ED visits", "Length of stay", "Medication count", "Rural distance"],
        "Value": [r.age, r.primary_condition, r.chronic_conditions, r.prior_admissions_12m, r.prior_ed_visits_12m, r.length_of_stay, r.medication_count, f"{r.rural_distance_miles} miles"],
    }, hide_index=True, use_container_width=True)
with right:
    st.markdown("### Leading contributors")
    drivers = top_drivers(r)
    ddf = {"Driver": drivers, "Relative rank": list(range(len(drivers), 0, -1))}
    st.plotly_chart(px.bar(ddf, x="Relative rank", y="Driver", orientation="h"), use_container_width=True)

st.markdown("### Suggested operational workflow")
st.success(r.suggested_workflow)
st.write("Additional review flags:")
flags = []
if r.followup_scheduled == "No": flags.append("Confirm post-discharge appointment")
if r.medication_count >= 10: flags.append("Medication reconciliation review")
if r.transportation_barrier == "Yes": flags.append("Assess transportation support")
if r.lives_alone == "Yes": flags.append("Assess social support and caregiver availability")
if r.home_health_referral == "No" and r.priority in ["High", "Critical"]: flags.append("Review possible care-coordination or home-support needs")
st.write(" • " + "\n • ".join(flags or ["No additional operational flags"]))
