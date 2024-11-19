import streamlit as st
from PIL import Image
from io import BytesIO
from time import sleep
from pathlib import Path
import json

from const.app_mode import IS_RELEASE_VERSION
from const.session_names import SessionNames as sn
from lib.utils.detect_file_attributes import detect_file_format
from lib.utils.uuid_generator import generate_random_uuid
from lib.utils.image_converter import merge_images_to_single_image, merge_mixed_files_to_single_image
from lib.utils.validator import validate_uploaded_files, try_fix_amount, try_fix_nip
from lib.google.vision_client import VisionClient
from lib.ai.openai_client import OpenAiClient, OpenAiStatus
from lib.io.file_manager import FileManager
from page.components.error.error_dialog import show_error
from page.func.switch_page import switch_page
from page.components.indicator.progress_bar import ProgressBar
from page.components.header.header import load_header


def switch_to_edit():
    st.session_state[sn.EDIT_INV_ACTION] = sn.EDIT_INV_ACTION_ADD
    switch_page("invoices_edit")


def load():
    if st.session_state[sn.EDIT_INV_ACTION] == sn.EDIT_INV_ACTION_UPDATE:
        load_header("Edycja faktury")
    else:
        load_header("Dodawanie faktur")
        # previously not saved yet
        if sn.NEW_INVOICES in st.session_state:
            if st.session_state[sn.NEW_INVOICES]:
                switch_to_edit()
        

    option_process = "Mam całe faktury w osobnych plikach (wynikiem będą te faktury)"
    option_merge = "Mam jedną fakturę w kilku plikach (wynikiem będzie jedna scalona faktura)"
    option = st.radio(
        label="Wybierz odpowiednią opcję:",
        options=[
            option_process,
            option_merge
        ]
    )

    allowed_file_types = ['pdf', 'png', 'jpeg', 'jpg']
    uploaded_files = st.file_uploader(
        label="Plik(i) faktury",
        type=allowed_file_types,
        accept_multiple_files=True, label_visibility="hidden",
        key="new_inv_files_uploader"
    )

    if st.button("Start", key="btn_process_files"):
        openai_api_key = st.session_state[sn.OPENAI_API_KEY]
        google_api_key = st.session_state[sn.GOOGLE_API_KEY]

        openai_status = OpenAiStatus.verify_model_support(openai_api_key)
        if openai_status != "OK":
            show_error(openai_status)
            st.stop()

        if uploaded_files or not IS_RELEASE_VERSION:
            progress_bar = ProgressBar(0.0, "Przygotowanie...")
                        
            varified_files_info = validate_uploaded_files(uploaded_files)
            if varified_files_info == "OK":
                files_cnt = len(uploaded_files)
                # create list of images for processing
                # PDF sites are merge to single image
                images = []
                for uploaded_file in uploaded_files:
                    if detect_file_format(uploaded_file) == "PDF":
                        image = merge_mixed_files_to_single_image([uploaded_file])
                    else:
                        image = Image.open(BytesIO(uploaded_file.read()))
                    images.append(image)
                    del uploaded_file # release file from memory
                
                # merge images when user chose 'one doc splited' option
                if (option == option_merge):
                    integrated_image = merge_images_to_single_image(images)
                    images_for_process = [integrated_image]
                else:
                    images_for_process = images
                
                # processing images
                try:
                    if IS_RELEASE_VERSION:
                        vision_client = VisionClient(google_api_key)
                        openai_client = OpenAiClient(openai_api_key)

                    if sn.NEW_INVOICES not in st.session_state:
                        st.session_state[sn.NEW_INVOICES] = []
                    new_invs = st.session_state[sn.NEW_INVOICES]

                    img_counter = 0

                    if not IS_RELEASE_VERSION:
                        with open('.result_1.json', 'r', encoding='utf-8') as f:
                            result_1 = json.load(f)
                        with open('.result_2.json', 'r', encoding='utf-8') as f:
                            result_2 = json.load(f)
                        files_cnt = 2

                    if IS_RELEASE_VERSION:
                        data_for_process = images_for_process
                    else:
                        data_for_process = result_1, result_2

                    for proc_data in data_for_process:
                        progress_bar.update_files_counter(img_counter, files_cnt)

                        if IS_RELEASE_VERSION:
                            ocr_text = vision_client.extract_text_from_image(proc_data)

                            img_filename = f'{generate_random_uuid()}.png'
                            fm = FileManager(crypt_key=st.session_state[sn.ENCRYPT_KEY])
                            fm.resize_and_save_invoice_image(Path(st.session_state[sn.DIR_INVOICES_IMAGES]) / img_filename, proc_data)
                            del proc_data # release image from memory

                            from_proc_data, usage = openai_client.get_invoice_info(ocr_text)
                            from_proc_json = json.loads(from_proc_data)
                        else:
                            from_proc_json = proc_data
                            img_filename = ""
                        
                        doc_counter = 1
                        for doc_json in from_proc_json:
                            new_inv = {}
                            for key, val in doc_json.items():
                                if key in [sn.INV_BUYER_NIP, sn.INV_SELLER_NIP]:
                                    val = try_fix_nip(val)
                                if key in [sn.INV_TOTAL_GROSS_AMOUNT, sn.INV_TOTAL_NET_AMOUNT, sn.INV_TOTAL_TAX_AMOUNT]:
                                    val = try_fix_amount(val)
                                
                                new_inv[key] = val
                            
                            doc_id = f"doc_{img_counter + 1}_{doc_counter}"
                            new_inv[sn.INV_DOC_ID] = f"{doc_id}"
                            new_inv[sn.INV_DOC_IMAGE] = img_filename
                            new_invs.append(new_inv)
                            doc_counter += 1

                        img_counter += 1
                    
                    progress_bar.update_files_counter(img_counter, files_cnt)
                    sleep(1)
                    progress_bar.empty()

                    switch_to_edit()

                except Exception as e:
                    show_error(e)

            else:
                show_error(varified_files_info)
        else:
            st.error("Wybierz plik(i) do przetworzenia")
