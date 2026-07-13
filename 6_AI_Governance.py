import streamlit as st
from utils.ui import page_header

st.set_page_config(page_title="AI Governance", page_icon="🛡️", layout="wide")
page_header("Responsible AI Governance", "Controls required before any real-world healthcare use")

st.markdown("### Intended use")
st.write("Support human prioritization of post-discharge review and care-coordination workflows. The tool is not intended to diagnose, prescribe, or replace clinical judgment.")

st.markdown("### Required safeguards")
st.markdown("""
- Use minimum-necessary data and execute a formal privacy and security review.
- Validate the model on local data before deployment.
- Require clinician and care-team review of every recommendation.
- Monitor false negatives, calibration, data drift, and subgroup performance.
- Document model version, training data period, thresholds, limitations, and ownership.
- Create an escalation and override process for users.
- Conduct usability testing with clinicians, nurses, compliance, IT, and patients where appropriate.
""")

st.markdown("### Demonstration boundaries")
st.error("No protected health information, no EHR connection, no autonomous clinical decision-making, and no treatment recommendations.")

st.markdown("### Suggested pilot approval path")
st.write("Clinical sponsor → Privacy/security → Compliance/legal → Data governance → Local validation → Limited silent pilot → Workflow evaluation → Controlled implementation.")
