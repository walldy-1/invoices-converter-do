import streamlit as st

from const.session_names import SessionNames as sn
from page.func.switch_page import switch_page

def load():
    

    col_margin_left, col_main, col_margin_right = st.columns([1, 1, 1])

    with col_main.container(border=True):
        st.markdown("# Witaj w Fakturowni!")
        st.markdown("")
        st.markdown("**Nie przepisuj swoich faktur do Excela!**")
        st.markdown("**Nasz dyżurny eSkryba zrobi to za Ciebie :smile:**")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("Co dalej?")
        st.markdown("<br>", unsafe_allow_html=True)

        col_margin_left, col_1, col_2, col_margin_2 = st.columns([1, 2, 2, 1])
        with col_1:
            if st.button("Mam konto", key="btn_have_acount"):
                st.session_state[sn.LOGIN_TYPE] = "user"
                switch_page("login")
                
        with col_2:
            if st.button("Zaloguj jako Gość", key="btn_continue_as_guest"):
                st.session_state[sn.LOGIN_TYPE] = "guest"
                switch_page("login")
