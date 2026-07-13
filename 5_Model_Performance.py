import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.data import load_data
from utils.ui import page_header

st.set_page_config(page_title="Model Performance", page_icon="📈", layout="wide")
page_header("Model Performance", "Holdout results from synthetic demonstration data")
root=Path(__file__).resolve().parents[1]
metrics=json.loads((root/"models"/"model_metrics.json").read_text())
best=metrics["best_model"]
m=metrics["metrics"][best]

c1,c2,c3,c4=st.columns(4)
c1.metric("Selected model", best)
c2.metric("Holdout AUC", f"{m['roc_auc']:.3f}")
c3.metric("Recall", f"{m['recall']:.1%}")
c4.metric("Precision", f"{m['precision']:.1%}")

comparison=pd.DataFrame([{"Model":name, **vals} for name,vals in metrics["metrics"].items()]).drop(columns=["confusion_matrix"])
st.markdown("### Candidate-model comparison")
st.dataframe(comparison,hide_index=True,use_container_width=True)

importance=pd.read_csv(root/"models"/"feature_importance.csv").head(10).sort_values("importance")
st.plotly_chart(px.bar(importance,x="importance",y="feature",orientation="h",title="Permutation importance on synthetic holdout data"),use_container_width=True)

df=load_data()
st.markdown("### Score distribution")
st.plotly_chart(px.histogram(df,x="readmission_probability",color="priority",nbins=20),use_container_width=True)

st.warning("All records and outcomes are synthetic. These metrics validate software behavior only and are not clinical evidence.")
