import streamlit as st

from const.session_names import SessionNames as sn
from page.func.page_inputs import prepare_inputs_session_structure
from page.components.invoice import edit_form
from page.components.header.header import load_header


def load():
    prepare_inputs_session_structure(st.session_state[sn.CURR_PAGE])
    
    action = st.session_state[sn.EDIT_INV_ACTION]
    if action == sn.EDIT_INV_ACTION_ADD:
        load_header("Dodawanie faktur")
        invs = st.session_state[sn.NEW_INVOICES]
    else:
        load_header("Edycja faktury")
        invs = st.session_state[sn.EXISTING_INVOICES]
    
    for inv in invs:
        edit_form.load(inv)

