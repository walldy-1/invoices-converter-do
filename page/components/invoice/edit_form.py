import streamlit as st
from pathlib import Path
from typing import Literal

from const.app_mode import IS_RELEASE_VERSION
from const.session_names import SessionNames as sn
from lib.utils.validator import convert_date_to_db_format as date_db
from lib.utils.validator import to_float
from lib.utils.image_converter import read_image
from lib.utils.uuid_generator import generate_random_uuid
from lib.io.file_manager import FileManager
from page.components.error.error_dialog import show_error_dialog
from page.func.switch_page import switch_page
from page.func.form_validator import(
    check_form_value,
    check_totals,
    check_doc,
    style_invalid_values_widgets
)


s_st = st.session_state

def prepare_widget_key(attr_name: str, doc_id: str) -> str:
    return f"inv_edit_{attr_name}__{doc_id}"


def prepare_widget(
        attr_name: str,
        attr_type: Literal["amount", "date", "nip", "other"],
        doc_id: str,
        widget_label: str,
        widget_value: str,
        inputs: dict,
        errors: dict):
    
    if attr_type == "date" and str(widget_value).lower() == "nat":
        widget_value = None
    if attr_type == "amount" and str(widget_value).lower() == "nan":
        widget_value = None

    widget_key = prepare_widget_key(attr_name, doc_id)
    max_length = 20
    
    # change attr type when amount is total price from invoice,
    # for extra validation
    if attr_name in [
        sn.INV_TOTAL_GROSS_AMOUNT,
        sn.INV_TOTAL_NET_AMOUNT,
        sn.INV_TOTAL_TAX_AMOUNT]:
        attr_type = "totals"

    if attr_type == "other":
        max_length = 100

    st.text_input(
        label=widget_label,
        value=widget_value,
        key=widget_key,
        max_chars=max_length
    )

    # set widget key in session doc members
    inputs[doc_id][attr_name] = widget_key
    
    # validate widget value
    if attr_type == "totals":
        pass
        #check_totals(doc_id, s_st[sn.CURR_PAGE], errors)
    else:
        check_form_value(attr_type, widget_key, errors)
    

def remove_doc_from_list(doc_id):
    if s_st[sn.EDIT_INV_ACTION] == sn.EDIT_INV_ACTION_ADD:
        invs = s_st[sn.NEW_INVOICES]
    else:
        invs = s_st[sn.EXISTING_INVOICES]
    
    invs[:] = [doc for doc in invs if doc[sn.INV_DOC_ID] != doc_id]

    if not invs:
        switch_page("invoices_view", with_rerun=False)


def save_doc(
        doc_id: str,
        img_filename: str,
        inputs: dict,
        errors: dict):
    
    if not check_doc(doc_id, inputs, errors):
        show_error_dialog("""
            Wszystkie pozycje faktury wyróżnione na czerwono
            muszą zostać poprawione lub usunięte przed zapisaniem.
            
        """)
        return

    doc_widgets_keys = inputs[doc_id].items()
    
    out_json = {sn.INV_DOC_IMAGE: img_filename}
    action = s_st[sn.EDIT_INV_ACTION]
    if action == sn.EDIT_INV_ACTION_ADD:
        out_json[sn.INV_DOC_ID] =  generate_random_uuid()
    else:
        out_json[sn.INV_DOC_ID] = doc_id
    
    for key, val in doc_widgets_keys:
        if key.endswith("date"):
            s_st[val] = date_db(s_st[val])
        if key.endswith("amount"):
            s_st[val] = to_float(s_st[val])
        if not s_st[val]:
            s_st[val] = None
        out_json.update({key: s_st[val]})

    path_doc = s_st[sn.DIR_INVOICES] / "invoices.json"
    fm = FileManager(crypt_key=s_st[sn.ENCRYPT_KEY])
    fm.save_invoice_data(path_doc, [out_json])
    remove_doc_from_list(doc_id)


def load(json_data):
    doc_id = json_data[sn.INV_DOC_ID]
    curr_page = s_st[sn.CURR_PAGE]

    inputs = s_st[sn.INPUT_WIDGETS][curr_page][sn.INPUT_WIDGETS_WIDGETS]
    errors = s_st[sn.INPUT_WIDGETS][curr_page][sn.INPUT_WIDGETS_ERRORS]
    
    # set doc widgets members
    if doc_id not in inputs:
        inputs[doc_id] = {}
    
    with st.container(border=True):
        (col_margin_left,
        col_form,
        col_between_1,
        #col_between_2,
        col_image,
        col_margin_right) = st.columns([1, 8, 1, 8, 1])

        with col_margin_left:
            st.button(
                label="X",
                key=f"btn_remove_{doc_id}",
                on_click=lambda: remove_doc_from_list(doc_id),
                help="Odrzuć"
            )

        with col_form.container():
            col_1_1, col_1_2, col_1_3 = st.columns([1, 2, 1])

            with col_1_1:
                prepare_widget(
                    attr_name=sn.INV_DOC_TYPE,
                    attr_type="other",
                    doc_id=doc_id,
                    widget_label="Typ dokumentu",
                    widget_value=json_data[sn.INV_DOC_TYPE],
                    inputs=inputs,
                    errors=errors
                )
            with col_1_2:
                prepare_widget(
                    attr_name=sn.INV_DOC_NUMBER,
                    attr_type="other",
                    doc_id=doc_id,
                    widget_label="Nr dokumentu",
                    widget_value=json_data[sn.INV_DOC_NUMBER],
                    inputs=inputs,
                    errors=errors
                )
            with col_1_3:
                prepare_widget(
                    attr_name=sn.INV_ISSUE_DATE,
                    attr_type="date",
                    doc_id=doc_id,
                    widget_label="Data wystawienia",
                    widget_value=json_data[sn.INV_ISSUE_DATE],
                    inputs=inputs,
                    errors=errors
                )

            col_2_1, col_2_2 = st.columns([1, 3])
            with col_2_1:
                prepare_widget(
                    attr_name=sn.INV_SELLER_NIP,
                    attr_type="nip",
                    doc_id=doc_id,
                    widget_label="NIP sprzedawcy",
                    widget_value=json_data[sn.INV_SELLER_NIP],
                    inputs=inputs,
                    errors=errors
                )
            with col_2_2:
                prepare_widget(
                    attr_name=sn.INV_SELLER_ADDRESS,
                    attr_type="other",
                    doc_id=doc_id,
                    widget_label="Adres sprzedawcy",
                    widget_value=json_data[sn.INV_SELLER_ADDRESS],
                    inputs=inputs,
                    errors=errors
                )

            prepare_widget(
                attr_name=sn.INV_SELLER_NAME,
                attr_type="other",
                doc_id=doc_id,
                widget_label="Nazwa sprzedawcy",
                widget_value=json_data[sn.INV_SELLER_NAME],
                inputs=inputs,
                errors=errors
            )

            col_3_1, col_3_2 = st.columns([1, 3])
            with col_3_1:
                prepare_widget(
                    attr_name=sn.INV_BUYER_NIP,
                    attr_type="nip",
                    doc_id=doc_id,
                    widget_label="NIP nabywcy",
                    widget_value=json_data[sn.INV_BUYER_NIP],
                    inputs=inputs,
                    errors=errors
                )
            with col_3_2:
                prepare_widget(
                    attr_name=sn.INV_BUYER_ADDRESS,
                    attr_type="other",
                    doc_id=doc_id,
                    widget_label="Adres nabywcy",
                    widget_value=json_data[sn.INV_BUYER_ADDRESS],
                    inputs=inputs,
                    errors=errors
                )
                
            prepare_widget(
                attr_name=sn.INV_BUYER_NAME,
                attr_type="other",
                doc_id=doc_id,
                widget_label="Nazwa nabywcy",
                widget_value=json_data[sn.INV_BUYER_NAME],
                inputs=inputs,
                errors=errors
            )

            col_4_1, col_4_2, col_4_3 = st.columns(3)
            with col_4_1:
                prepare_widget(
                    attr_name=sn.INV_TOTAL_NET_AMOUNT,
                    attr_type="amount",
                    doc_id=doc_id,
                    widget_label="Wartość NETTO",
                    widget_value=json_data[sn.INV_TOTAL_NET_AMOUNT],
                    inputs=inputs,
                    errors=errors
                )
                
            with col_4_2:
                prepare_widget(
                    attr_name=sn.INV_TOTAL_TAX_AMOUNT,
                    attr_type="amount",
                    doc_id=doc_id,
                    widget_label="Wartość VAT",
                    widget_value=json_data[sn.INV_TOTAL_TAX_AMOUNT],
                    inputs=inputs,
                    errors=errors
                )

            with col_4_3:
                prepare_widget(
                    attr_name=sn.INV_TOTAL_GROSS_AMOUNT,
                    attr_type="amount",
                    doc_id=doc_id,
                    widget_label="Wartość BRUTTO",
                    widget_value=json_data[sn.INV_TOTAL_GROSS_AMOUNT],
                    inputs=inputs,
                    errors=errors
                )
            
            with st.columns(5)[2]:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button(
                    label="Zapisz",
                    key=f"btn_save_{doc_id}",
                    on_click=lambda: save_doc(doc_id, json_data[sn.INV_DOC_IMAGE], inputs, errors)
                )

        img_height = 600
        with col_image.container(height=img_height, border=True):
            if IS_RELEASE_VERSION:
                img_path = Path(s_st[sn.DIR_INVOICES_IMAGES]) / json_data[sn.INV_DOC_IMAGE]
                image = read_image(img_path)
                st.image(image, use_container_width=True)
            else:
                st.components.v1.html(f"""
                    <div style="display: flex; align-items: center; justify-content: center; height: {img_height}px;">
                        <p style="font-size: 18px; color: grey;">Brak obrazu</p>
                    </div>
                    """, height=img_height)
            
    style_invalid_values_widgets(errors)
