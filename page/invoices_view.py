import streamlit as st
import pandas as pd
from pathlib import Path
from pandas import DataFrame
from typing import Tuple, Literal
from datetime import datetime

from const.session_names import SessionNames as sn
from const.invoice import InvoiceVarNames as inm
from const.invoice import InvoiceDateFormats
from lib.io.file_manager import FileManager
from lib.utils.validator import try_fix_amount
from page.components.header.header import load_header
from page.components.invoice.export_dialog import show_export_dialog
from page.func.page_inputs import prepare_inputs_session_structure
from page.func.switch_page import switch_page
from page.func.form_validator import(
    check_amount,
    check_date,
    style_invalid_values_widgets,
    validate_amount,
    validate_date,
    to_float,
)


s_st = st.session_state

def get_db_inv_data() -> DataFrame:
    db_path = Path(st.session_state[sn.DIR_INVOICES]) / "invoices.json"
    fm = FileManager(crypt_key=st.session_state[sn.ENCRYPT_KEY])
    return fm.read_invoice_data(db_path, "df")


def df_selected(data_df: DataFrame, ids_df: DataFrame):
    amount_cols = [
        inm.INV_TOTAL_GROSS_AMOUNT,
        inm.INV_TOTAL_NET_AMOUNT,
        inm.INV_TOTAL_TAX_AMOUNT
    ]
    sel_row_state = st.session_state["df_inv_view"]["selection"]["rows"]
    if len(sel_row_state) > 0:
        idx = sel_row_state[0]
        inv_data = data_df.loc[idx].to_dict()
        inv_id = ids_df.loc[idx][sn.INV_DOC_ID]
        inv_image = ids_df.loc[idx][sn.INV_DOC_IMAGE]
        inv_data[sn.INV_DOC_ID] = inv_id
        inv_data[sn.INV_DOC_IMAGE] = inv_image
        s_st[sn.EDIT_INV_ACTION] = "edit"
        s_st[sn.EXISTING_INVOICES] = [inv_data]

        for key, val in inv_data.items():
            if key in amount_cols:
                inv_data[key] = try_fix_amount(val)

        switch_page("invoices_edit", with_rerun=False)


def get_filter(filter_widget_key: str) -> str | None:
    return st.session_state.get(filter_widget_key, None)


def get_data() -> Tuple[DataFrame, DataFrame]:
    text_search = get_filter(sn.INV_FILTER_TEXT_WIDGET_KEY)
    start_date = get_filter(sn.INV_FILTER_DATE_FROM_WIDGET_KEY)
    end_date = get_filter(sn.INV_FILTER_DATE_TO_WIDGET_KEY)
    min_amount = get_filter(sn.INV_FILTER_TOTAL_GROSS_AMOUNT_FROM_WIDGET_KEY)
    max_amount = get_filter(sn.INV_FILTER_TOTAL_GROSS_AMOUNT_TO_WIDGET_KEY)

    data = get_db_inv_data()
    if data is None:
        switch_page("invoices_add")
    
    df = data

    # starter filter mask - all rows
    mask = pd.Series(True, index=df.index)

    # text mask
    if text_search:
        cols_text_search = [
            inm.INV_DOC_NUMBER,
            inm.INV_SELLER_NIP,
            inm.INV_SELLER_ADDRESS,
            inm.INV_SELLER_NAME,
            inm.INV_BUYER_NIP,
            inm.INV_BUYER_ADDRESS,
            inm.INV_BUYER_NAME
        ]
        text_mask = (
            df[cols_text_search]
            .apply(lambda col: col.str.lower().str.contains(text_search.lower(), na=False))
            .any(axis=1)
        )
        mask &= text_mask

    # dates masks
    date_format = InvoiceDateFormats.DB_FORMAT
    if start_date and validate_date(start_date, db_format_only=True):
        start_date = datetime.strptime(start_date, date_format).date()
        mask &= (df[inm.INV_ISSUE_DATE] >= start_date)
    if end_date and validate_date(end_date, db_format_only=True):
        end_date = datetime.strptime(end_date, date_format).date()
        mask &= (df[inm.INV_ISSUE_DATE] <= end_date)

    # amounts masks
    if min_amount and validate_amount(min_amount):
        mask &= (df[inm.INV_TOTAL_GROSS_AMOUNT] >= to_float(min_amount))
    if max_amount and validate_amount(max_amount):
        mask &= (df[inm.INV_TOTAL_GROSS_AMOUNT] <= to_float(max_amount))
    
    # preparing data
    sort_cols = [inm.INV_ISSUE_DATE]
    filtered_df = (
        df[mask][[
            inm.INV_DOC_TYPE,
            inm.INV_DOC_NUMBER,
            inm.INV_ISSUE_DATE,
            inm.INV_TOTAL_NET_AMOUNT,
            inm.INV_TOTAL_TAX_AMOUNT,
            inm.INV_TOTAL_GROSS_AMOUNT,
            inm.INV_SELLER_NIP,
            inm.INV_SELLER_NAME,
            inm.INV_SELLER_ADDRESS,
            inm.INV_BUYER_NIP,
            inm.INV_BUYER_NAME,
            inm.INV_BUYER_ADDRESS,
            inm.INV_DOC_ID,
            inm.INV_DOC_IMAGE
        ]]
        .sort_values(by=sort_cols, ascending=False).reset_index(drop=True)
    )

    # not displayed columns
    hidden_cols = [inm.INV_DOC_ID, inm.INV_DOC_IMAGE]
    hidden_df = filtered_df[hidden_cols].copy()
    filtered_df.drop(columns=hidden_cols, inplace=True)

    # styling data
    amount_format = "{:,.2f}"
    amount_cols = [
        inm.INV_TOTAL_GROSS_AMOUNT,
        inm.INV_TOTAL_NET_AMOUNT,
        inm.INV_TOTAL_TAX_AMOUNT
    ]
    # format_dict = {col: amount_format for col in amount_cols}
    # filtered_df.style.format(format_dict, thousands=" ", decimal=",")

    # amounts formatting
    for col in amount_cols:
        filtered_df[col] = filtered_df[col].apply(lambda x: amount_format.format(x).replace(',', ' ').replace('.', ','))

    # st.write(filtered_df)
    # st.stop()

    return filtered_df, hidden_df


def clear_filters():
    s_st[get_filter_memory_key(sn.INV_FILTER_TEXT_WIDGET_KEY)] = ""
    s_st[get_filter_memory_key(sn.INV_FILTER_DATE_FROM_WIDGET_KEY)] = ""
    s_st[get_filter_memory_key(sn.INV_FILTER_DATE_TO_WIDGET_KEY)] = ""
    s_st[get_filter_memory_key(sn.INV_FILTER_TOTAL_GROSS_AMOUNT_FROM_WIDGET_KEY)] = ""
    s_st[get_filter_memory_key(sn.INV_FILTER_TOTAL_GROSS_AMOUNT_TO_WIDGET_KEY)] = ""


def get_filter_memory_key(widget_key: str) -> str:
    return widget_key.replace("txt_", "")


def get_filter_memory_value(widget_key: str) -> str:
    memory_key = get_filter_memory_key(widget_key)
    return s_st.get(memory_key, "")


def save_filter(widget_key: str):
    memory_key = get_filter_memory_key(widget_key)
    s_st[memory_key] = s_st[widget_key]


def load_filter_widget(
        label: str,
        key: str,
        type: Literal["amount", "date", "other"],
        errors: dict
):
    placeholder = "Wszystkie"
    max_chars = 20
    value = get_filter_memory_value(key)
    on_change_callback = lambda: save_filter(key)
    check_func = None

    if type == "amount":
        check_func = lambda: check_amount(key, errors)
    elif type == "date":
        max_chars = 10
        placeholder = "RRRR-MM-DD"
        check_func = lambda: check_date(key, errors, db_format_only=True)

    st.text_input(
        label=label,
        key=key,
        max_chars=max_chars,
        placeholder=placeholder,
        value=value,
        on_change=on_change_callback
    )

    if check_func:
        check_func()


def load_filters(errors: dict):
    with st.container(border=True):
        col_filters, col_space, col_export = st.columns([8, 1, 3])
        with col_filters.container():
            with st.columns([3, 1, 3])[1]:
                st.markdown("###### Filtry")

            (col_text,
             col_date_from,
             col_date_to,
             col_amount_from,
             col_amount_to,
             col_clear) = st.columns([2, 1, 1, 1, 1, 1])
            
            with col_text.container():
                load_filter_widget(
                    label="Dane kontrahentów, Numer fakt.",
                    key=sn.INV_FILTER_TEXT_WIDGET_KEY,
                    type="other",
                    errors=errors
                )
            with col_date_from.container():
                load_filter_widget(
                    label="Data od",
                    key=sn.INV_FILTER_DATE_FROM_WIDGET_KEY,
                    type="date",
                    errors=errors
                )
            with col_date_to.container():
                load_filter_widget(
                    label="Data do",
                    key=sn.INV_FILTER_DATE_TO_WIDGET_KEY,
                    type="date",
                    errors=errors
                )
            with col_amount_from.container():
                load_filter_widget(
                    label="Brutto min",
                    key=sn.INV_FILTER_TOTAL_GROSS_AMOUNT_FROM_WIDGET_KEY,
                    type="amount",
                    errors=errors
                )
            with col_amount_to.container():
                load_filter_widget(
                    label="Brutto maks",
                    key=sn.INV_FILTER_TOTAL_GROSS_AMOUNT_TO_WIDGET_KEY,
                    type="amount",
                    errors=errors
                )
            with col_clear:
                st.button(
                    label="X",
                    help="Wyczyść filtry",
                    key="btn_clear_filters",
                    on_click=clear_filters
                )


def load():
    load_header("Przegląd faktur")

    curr_page = s_st[sn.CURR_PAGE]
    prepare_inputs_session_structure(curr_page)
    errors = s_st[sn.INPUT_WIDGETS][curr_page][sn.INPUT_WIDGETS_ERRORS]
    
    load_filters(errors)
    filtered_df, hidden_df = get_data()

    if st.button('Pobierz'):
        show_export_dialog(filtered_df)
    
    st.dataframe(
        data=filtered_df,
        selection_mode="single-row",
        on_select=lambda: df_selected(filtered_df, hidden_df),
        key="df_inv_view",
        use_container_width=True,
        height=500,
        hide_index=True,
        column_config={
            "doc_type": st.column_config.Column("Typ", width="small"),
            "doc_number": st.column_config.Column("Numer", width="small"),
            "issue_date": st.column_config.Column("Data", width=None),
            "seller_nip": st.column_config.Column("NIP sprzed.", width=None),
            "seller_address": st.column_config.Column("Adres sprzedawcy", width="medium"),
            "seller_name": st.column_config.Column("Nazwa sprzedawcy", width="medium"),
            "buyer_nip": st.column_config.Column("NIP nab.", width=None),
            "buyer_address": st.column_config.Column("Adres nabywcy", width="medium"),
            "buyer_name": st.column_config.Column("Nazwa nabywcy", width="medium"),
            "total_net_amount": st.column_config.Column("NETTO", width=None),
            "total_tax_amount": st.column_config.Column("VAT", width=None),
            "total_gross_amount": st.column_config.Column("BRUTTO", width=None)
        }
    )

    style_invalid_values_widgets(errors)
