import streamlit as st

from page.func.switch_page import switch_page


def load_navigation():
    col_margin_left, col_center, col_margin_right = st.columns([1, 4, 1])

    with col_center:
        st.button(
            label="Przeglądaj faktury",
            on_click=lambda: switch_page("invoices_view", with_rerun=False),
            use_container_width=True,
            key="btn_nav_invoices_view"
        )
        
        st.button(
            label="Dodaj faktury",
            on_click=lambda: switch_page("invoices_add", with_rerun=False),
            use_container_width=True,
            key="btn_nav_invoices_add"
        )
