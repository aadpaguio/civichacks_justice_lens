import streamlit as st

from shared_styles import inject_css, sidebar_page_links

inject_css()
sidebar_page_links()

st.title("Data")
st.divider()

st.write("Add your data tables or uploads here.")
