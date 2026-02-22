"""
Dashboard – main entry. Redirects to first page.
Run with: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Justice Lens",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# No main page content — go straight to first dashboard
st.switch_page("pages/police_misconduct.py")
