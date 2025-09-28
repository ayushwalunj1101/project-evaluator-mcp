import streamlit as st

st.set_page_config(
    page_title="Unified IP Analysis Platform",
    layout="wide"
)

st.title("📊 Unified IP Analysis Platform")
st.markdown("### All your tools in one place — choose a module below:")

module = st.radio(
    "Select a module:",
    ["Patentability", "Code Evaluation", "Innovation & Novelty", "Problem Solution fit"]
)

MODULE_PORTS = {
    "Patentability": 8502,
    "Innovation & Novelty": 8503,
    "Code Evaluation": 8504,
    "Problem Solution fit": 8501
}

if module:
    port = MODULE_PORTS[module]
    st.markdown(f"""
        <iframe src="http://localhost:{port}"
        width="100%" height="800" frameborder="0"></iframe>
    """, unsafe_allow_html=True)
