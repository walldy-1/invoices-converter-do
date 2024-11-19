import streamlit as st
from cryptography.fernet import Fernet

from const.session_names import SessionNames as sn
from lib.ai.openai_client import OpenAiStatus
from page.components.error.error_dialog import show_error_dialog
from lib.utils.uuid_generator import generate_random_uuid
from page.func.switch_page import switch_page
from lib.io.dir_creator import DirCreator


def load_guest_form():
    col_left_margin, col_main, col_right_margin = st.columns([1, 1, 1])
    with col_main:
        with st.form(key='guest_login_form'):
            openai_api_key = st.text_input(
                label="Twój klucz OpenAI",
                type="password",
                help="Podanie klucza jest niezbędne do działania aplikacji.\
                    Twój klucz nie jest nigdzie zapisywany."
            )

            col_1, col_2 = st.columns(2)
            with col_1:
                if st.form_submit_button("Zaloguj jako Gość"):
                    openai_status = OpenAiStatus.verify_model_support(openai_api_key)
                    if (openai_status == "OK"):
                        st.session_state[sn.IS_GUEST] = True
                        username = generate_random_uuid()
                        st.session_state[sn.USERNAME] = username
                        st.session_state[sn.OPENAI_API_KEY] = openai_api_key
                        google_api_key = st.secrets["googleApiKey"]
                        st.session_state[sn.GOOGLE_API_KEY] = google_api_key
                        crypt_key = Fernet.generate_key()
                        st.session_state[sn.ENCRYPT_KEY] = crypt_key
                        DirCreator.create_user_dirs(username)
                        st.session_state[sn.EDIT_INV_ACTION] = ""
                        switch_page("invoices_view")
                    else:
                        show_error_dialog(openai_status)
            
            with col_2:
                if st.form_submit_button("Powrót"):
                    switch_page("home")
