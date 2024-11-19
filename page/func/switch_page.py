import streamlit as st

from const.session_names import SessionNames as sn


def switch_page(new_page: str, with_rerun: bool = True) -> None:
    st.session_state[sn.CURR_PAGE] = new_page
    if with_rerun:
        st.rerun()