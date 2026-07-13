import streamlit as st
from utils.data import load_data
from utils.ui import page_header

st.set_page_config(page_title="Priority Worklist", page_icon="📋", layout="wide")
df = load_data()
page_header("Patient Priority Worklist", "Filter and prioritize synthetic post-discharge follow-up")

f1, f2, f3 = st.columns(3)
priorities = f1.multiselect("Priority", ["Routine", "Moderate", "High", "Critical"], default=["High", "Critical"])
conditions = f2.multiselect("Primary condition", sorted(df.primary_condition.unique()), default=[])
barrier = f3.selectbox("Transportation barrier", ["All", "Yes", "No"])

view = df[df.priority.isin(priorities)] if priorities else df.copy()
if conditions:
    view = view[view.primary_condition.isin(conditions)]
if barrier != "All":
    view = view[view.transportation_barrier == barrier]

view = view.sort_values(["risk_score", "prior_admissions_12m"], ascending=False)
cols = ["patient_id", "age", "primary_condition", "risk_score", "priority", "readmission_probability", "top_drivers", "suggested_workflow"]
st.dataframe(view[cols], use_container_width=True, hide_index=True, column_config={
    "readmission_probability": st.column_config.NumberColumn("Modeled probability", format="%.1%%"),
    "risk_score": st.column_config.ProgressColumn("Risk score", min_value=0, max_value=100),
})

st.download_button("Download filtered worklist", view[cols].to_csv(index=False), "synthetic_priority_worklist.csv", "text/csv")
