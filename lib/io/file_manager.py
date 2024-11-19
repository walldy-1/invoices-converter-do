import streamlit as st
import json
import pandas as pd
from cryptography.fernet import Fernet
from pandas import DataFrame
from pathlib import Path
from typing import Literal
from PIL import Image
from io import BytesIO


from const.app_mode import ENCRYPT_FILES
from const.session_names import SessionNames as sn
from const.invoice import InvoiceVarNames as inm
from lib.utils.image_converter import resize_invoice_image


class FileManager:
    def __init__(self, with_crypt: bool = True, crypt_key: str = None):
        if with_crypt and not crypt_key:
            raise ValueError("Missing 'crypt_key' value")
        
        is_guest = st.session_state.get(sn.IS_GUEST, False)

        self.with_crypt = with_crypt and ENCRYPT_FILES and is_guest
        if self.with_crypt:
            self.cipher = Fernet(crypt_key)


    def _encrypt_data(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)


    def _decrypt_data(self, data: bytes) -> bytes:
        return self.cipher.decrypt(data)


    def read_invoice_data(
            self,
            file_path: Path,
            format: Literal["dict", "df"] = "dict"
        ) -> list[dict] | DataFrame | None:

        if not Path.exists(file_path):
            return None

        mode = "rb" if self.with_crypt else "r"
        with open(file_path, mode) as file:
            data = file.read()
        
        if self.with_crypt:
            data = self._decrypt_data(data)

        json_data = json.loads(data)

        if format == "df":
            df = DataFrame(json_data)
            date_col = inm.INV_ISSUE_DATE
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            return df
        elif format == "dict":
            return json_data
        else:
            raise ValueError("'format' parameter must be 'dict' or 'df'")


    def save_invoice_data(
            self,
            file_path: Path, data: list[dict] | DataFrame):
        
        if isinstance(data, DataFrame):
            data = data.to_dict(orient="records")

        existing_data = self.read_invoice_data(file_path, "dict") or []

        # existing data
        data_dict = {item[inm.INV_DOC_ID]: item for item in existing_data}

        # add or update data
        for item in data:
            data_dict[item[inm.INV_DOC_ID]] = item

        # save updated data
        updated_data = list(data_dict.values())
        json_data = json.dumps(updated_data)
        mode = "wb" if self.with_crypt else "w"
        if self.with_crypt:
            json_data = self._encrypt_data(json_data.encode('utf-8'))

        with open(file_path, mode) as file:
            file.write(json_data)


    def read_invoice_image(self, image_path: Path) -> Image.Image:
        with open(image_path, "rb") as file:
            image_bytes = file.read()

        if self.with_crypt:
            image_bytes = self._decrypt_data(image_bytes)

        image = Image.open(BytesIO(image_bytes))
        return image


    def save_invoice_image(self, image_path: Path, image_data: Image.Image):
        bytes_io = BytesIO()
        image_data.save(bytes_io, format="PNG")
        image_bytes = bytes_io.getvalue()

        if self.with_crypt:
            image_bytes = self._encrypt_data(image_bytes)

        with open(image_path, "wb") as file:
            file.write(image_bytes)


    def resize_and_save_invoice_image(
            self,
            image_path: Path,
            image_data: Image.Image
    ):
        resized_img = resize_invoice_image(image_data)
        self.save_invoice_image(image_path, resized_img)
