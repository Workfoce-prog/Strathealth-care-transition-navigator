import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)
    st.info("Demonstration only. Uses synthetic data and does not provide diagnosis or treatment recommendations.")
