import streamlit as st
from typing import Literal

from const.session_names import SessionNames as sn
from lib.utils.validator import(
    validate_amount,
    validate_nip,
    validate_date,
    to_float
)


def set_invalid_value_widget_key(
        widget_key: str,
        is_value_valid: bool,
        errors: dict):
    
    if is_value_valid:
        if widget_key in errors:
            del errors[widget_key]
    else:
        errors[widget_key] = True


def is_valid_amount(value: str) -> bool:
    return validate_amount(str(value)) if value else True


def is_valid_nip(value: str) -> bool:
    return validate_nip(value) if value else True


def is_valid_date(value: str, db_format_only: bool = False) -> bool:
    return validate_date(value, db_format_only) if value else True


def check_amount(widget_key: str, errors: dict) -> bool:
    is_valid = is_valid_amount(str(st.session_state[widget_key]))
    set_invalid_value_widget_key(widget_key, is_valid, errors)
    return is_valid


def check_nip(widget_key: str, errors: dict) -> bool:
    is_valid = is_valid_nip(st.session_state[widget_key])
    set_invalid_value_widget_key(widget_key, is_valid, errors)
    return is_valid


def check_date(
        widget_key: str,
        errors: dict,
        db_format_only: bool = False) -> bool:
    
    is_valid = is_valid_date(st.session_state[widget_key], db_format_only)
    set_invalid_value_widget_key(widget_key, is_valid, errors)
    return is_valid


def check_totals(doc_id: str, page: str, errors: dict) -> bool:
    doc_widgets_keys = st.session_state[sn.INPUT_WIDGETS][page][sn.INPUT_WIDGETS_WIDGETS][doc_id]
    
    net_widget_key = None
    gross_widget_key = None
    tax_widget_key = None
    if sn.INV_TOTAL_NET_AMOUNT in doc_widgets_keys:
        net_widget_key = doc_widgets_keys[sn.INV_TOTAL_NET_AMOUNT]
    if sn.INV_TOTAL_GROSS_AMOUNT in doc_widgets_keys:
        gross_widget_key = doc_widgets_keys[sn.INV_TOTAL_GROSS_AMOUNT]
    if sn.INV_TOTAL_TAX_AMOUNT in doc_widgets_keys:
        tax_widget_key = doc_widgets_keys[sn.INV_TOTAL_TAX_AMOUNT]

    # values of totals widgets
    net_val = None
    gross_val = None
    tax_val = None
    if net_widget_key in st.session_state:
        net_val = st.session_state[net_widget_key]
    if gross_widget_key in st.session_state:
        gross_val = st.session_state[gross_widget_key]
    if tax_widget_key in st.session_state:
        tax_val = st.session_state[tax_widget_key]
    
    # check if all totals are valid and not empty for sum check
    # (empty value is acceptable for saving, but not for summation)
    # if single total is invalid, will be mark by check_amount()
    is_valid_net = check_amount(net_widget_key, errors) if net_val else False
    is_valid_gross = check_amount(gross_widget_key, errors) if gross_val else False
    is_valid_tax = check_amount(tax_widget_key, errors) if tax_val else False
    
    # marking all totals when net+tax is not equal gross
    if (all([is_valid_net, is_valid_gross, is_valid_tax])):
        net = to_float(net_val)
        gross = to_float(gross_val)
        tax =  to_float(tax_val)
        if gross != sum([net, tax]):
            set_invalid_value_widget_key(net_widget_key, False, errors)
            set_invalid_value_widget_key(gross_widget_key, False, errors)
            set_invalid_value_widget_key(tax_widget_key, False, errors)


def check_form_value(
        attr_type: Literal["amount", "date", "nip"],
        widget_key: str,
        errors: dict):

    if attr_type == "amount":
        check_amount(widget_key, errors)
    elif attr_type == "date":
        check_date(widget_key, errors)
    elif attr_type == "nip":
        check_nip(widget_key, errors)


def check_doc(doc_id: str, inputs: dict, errors: dict) -> bool:
    for input_key in inputs[doc_id].values():
        if input_key in errors:
            return False

    return True



def style_invalid_values_widgets(errors: str):
    widget_error_styles = "<style>"
    for key in errors:
        widget_error_styles += f"""\n
            .st-key-{key} input {{
                background-color: #ffcccc;
                color: #000000;
                font-weight: bold;
            }}
        """
    widget_error_styles += "</style>"
    st.markdown(widget_error_styles, unsafe_allow_html=True)
