import streamlit as st

from const.session_names import SessionNames as sn
from lib.io.dir_creator import DirCreator


def logout():
    if sn.IS_GUEST in st.session_state:
        if st.session_state[sn.IS_GUEST]:
            DirCreator.remove_user_dirs(st.session_state[sn.USERNAME])
            
    st.session_state.clear()
    st.rerun()
