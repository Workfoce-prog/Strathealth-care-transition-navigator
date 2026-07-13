import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics import confusion_matrix, roc_auc_score
from utils.data import load_data
from utils.ui import page_header

st.set_page_config(page_title="Model Performance", page_icon="📈", layout="wide")
df = load_data()
page_header("Model Performance", "Illustrative validation metrics for demonstration purposes")

rng = np.random.default_rng(42)
y_prob = df.readmission_probability.to_numpy()
y_true = rng.binomial(1, y_prob)
y_pred = (y_prob >= 0.30).astype(int)
auc = roc_auc_score(y_true, y_prob) if len(set(y_true)) > 1 else float("nan")
tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Illustrative AUC", f"{auc:.2f}")
c2.metric("Sensitivity", f"{tp/(tp+fn):.1%}" if tp+fn else "N/A")
c3.metric("Specificity", f"{tn/(tn+fp):.1%}" if tn+fp else "N/A")
c4.metric("Positive predictive value", f"{tp/(tp+fp):.1%}" if tp+fp else "N/A")

cal = pd.DataFrame({"probability": y_prob, "outcome": y_true})
cal["decile"] = pd.qcut(cal.probability, q=8, duplicates="drop")
cal = cal.groupby("decile", observed=True).agg(predicted=("probability", "mean"), observed=("outcome", "mean"), n=("outcome", "size")).reset_index()
st.plotly_chart(px.line(cal, x="predicted", y="observed", markers=True, title="Illustrative calibration"), use_container_width=True)

st.markdown("### Subgroup monitoring")
df2 = df.assign(simulated_outcome=y_true)
summary = df2.groupby("sex", as_index=False).agg(mean_score=("risk_score", "mean"), observed_rate=("simulated_outcome", "mean"), patients=("patient_id", "count"))
st.dataframe(summary, use_container_width=True, hide_index=True)

st.warning("These metrics are generated from synthetic outcomes and must not be interpreted as clinical evidence.")
