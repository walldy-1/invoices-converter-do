import streamlit as st

from const.session_names import SessionNames as sn
from page.components.header.header import load_header
from page.components.login_forms.login_guest_form import load_guest_form
from page.components.login_forms.login_user_form import load_user_form


def load():
    load_header("Logowanie")

    if (st.session_state[sn.LOGIN_TYPE] == "user"):
        load_user_form()
    else:
        load_guest_form()
