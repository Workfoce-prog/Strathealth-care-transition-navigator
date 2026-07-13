# StratHealth AI — Care Transition Navigator

A Streamlit demonstration of explainable post-discharge risk and follow-up prioritization using synthetic data.

## Features
- Executive dashboard
- Prioritized patient worklist
- Patient-level risk explanations
- Illustrative intervention simulator
- Model-performance monitoring
- Responsible AI governance page

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload all project files while preserving the folders.
3. In Streamlit Community Cloud, choose the repository and set the main file path to `app.py`.
4. Deploy.

## Important
This prototype uses only synthetic data. It is not a medical device, has not been clinically validated, and does not provide diagnosis or treatment recommendations.
