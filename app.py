import streamlit as st

from const.session_names import SessionNames as sn
from page.components.navigation.navigation import load_navigation
from page.components.error.error_dialog import show_error
from page.func.logout import logout

st.set_page_config(layout="wide")

if sn.CURR_PAGE not in st.session_state:
    st.session_state[sn.CURR_PAGE] = "home"


page = st.session_state[sn.CURR_PAGE]

if page == "home":
    from page import home
    home.load()

elif page == "invoices_add":
    from page import invoices_add
    invoices_add.load()

elif page == "invoices_view":
    from  page import invoices_view
    invoices_view.load()

elif page == "login":
    from  page import login
    login.load()

elif page == "invoices_edit":
    from page import invoices_edit
    invoices_edit.load()

else:
    show_error("Wystąpił nieznany błąd...")

if page not in ['home', 'login']:
    with st.sidebar:
        if st.button("Wyloguj"):
            logout()

        st.markdown("<br><br>", unsafe_allow_html=True)    
        load_navigation()
