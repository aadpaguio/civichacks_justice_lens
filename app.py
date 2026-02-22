"""
Dashboard – main entry.
Run with: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.header("Navigation")
    st.caption("Use the list above to switch pages.")
    st.divider()

st.title("📊 Dashboard")
st.markdown("Welcome. Use the sidebar to switch between pages.")
st.divider()

# Placeholder for home content
st.info("Select a page from the sidebar to get started.")
