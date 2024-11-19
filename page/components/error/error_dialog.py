import streamlit as st

from const.app_mode import IS_RELEASE_VERSION
from page.components.error.error_html import prepare_html_err_message


@st.dialog("Wystąpił błąd")
def show_error_dialog(message):
    msg = prepare_html_err_message(message)
    st.markdown(msg, unsafe_allow_html=True)


def show_error(message):
    if IS_RELEASE_VERSION:
        show_error_dialog(message)
    else:
        st.markdown(message)
