import streamlit as st

def load_header(header_text: str):
    with st.columns([3, 1, 3])[1]:
        st.markdown(f"##### {header_text}")
