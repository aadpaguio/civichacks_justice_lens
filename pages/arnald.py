import streamlit as st

st.title("Overview")
st.divider()

# Placeholder
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Metric A", "—", "—")
with col2:
    st.metric("Metric B", "—", "—")
with col3:
    st.metric("Metric C", "—", "—")

st.write("Add your overview content here.")
