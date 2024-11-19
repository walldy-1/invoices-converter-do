import streamlit as st

from const.session_names import SessionNames as sn


def prepare_inputs_session_structure(page: str):
    if sn.INPUT_WIDGETS not in st.session_state:
        st.session_state[sn.INPUT_WIDGETS] = {}
    
    inputs = st.session_state[sn.INPUT_WIDGETS]

    if page not in inputs:
        inputs[page] = {}
    
    if sn.INPUT_WIDGETS_WIDGETS not in inputs[page]:
        inputs[page][sn.INPUT_WIDGETS_WIDGETS] = {}

    if sn.INPUT_WIDGETS_ERRORS not in inputs[page]:
        inputs[page][sn.INPUT_WIDGETS_ERRORS] = {}
