import streamlit as st

from const.app_mode import IS_RELEASE_VERSION
from const.session_names import SessionNames as sn
from page.components.error.error_dialog import show_error_dialog
from page.func.switch_page import switch_page
from lib.io.dir_creator import DirCreator


def check_login(username, password):
    user_data = st.secrets.get(username)
    return user_data is not None and user_data["password"] == password


def load_user_form():
    col_left_margin, col_main, col_right_margin = st.columns([1, 1, 1])
    with col_main:
        with st.form(key='user_login_form'):
            if (IS_RELEASE_VERSION):
                username = st.text_input(label="Nazwa użytkownika")
                password = st.text_input(label="Hasło", type="password")
            else:
                username = st.text_input(
                    label="Nazwa użytkownika",
                    value="waldek"
                )
                password = st.text_input(
                    label="Hasło",
                    type="password",
                    value=st.secrets.get("waldek")["password"]
                )

            col_1, col_2 = st.columns(2)
            with col_1:
                if st.form_submit_button("Zaloguj"):
                    if check_login(username, password):
                        st.session_state[sn.LOGGED_IN] = True
                        st.session_state[sn.USERNAME] = username
                        secrets = st.secrets.get(username)
                        openai_api_key = secrets["openAiApiKey"]
                        st.session_state[sn.OPENAI_API_KEY] = openai_api_key
                        google_api_key = st.secrets["googleApiKey"]
                        st.session_state[sn.GOOGLE_API_KEY] = google_api_key
                        crypt_key = str(secrets["cryptKey"]).encode()
                        st.session_state[sn.ENCRYPT_KEY] = crypt_key
                        DirCreator.create_user_dirs(username)
                        st.session_state[sn.EDIT_INV_ACTION] = ""
                        switch_page("invoices_view")
                    else:
                        show_error_dialog("Niepoprawna nazwa użytkownika lub hasło.")
            with col_2:
                if st.form_submit_button("Powrót"):
                    switch_page("home")