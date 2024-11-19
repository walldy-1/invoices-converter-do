import imghdr
from io import BytesIO
from typing import Union, Tuple
from PIL import Image, UnidentifiedImageError
from streamlit.runtime.uploaded_file_manager import UploadedFile


def is_pdf_file_format(file_obj: BytesIO) -> bool:
    file_obj.seek(0)
    return file_obj.read(4) == b'%PDF'


def detect_file_attributes(
        file_obj: Union[BytesIO, UploadedFile, bytes]
    ) -> Tuple[str, str, bool]:

    file_type = "UNKNOWN"
    file_format = None
    pillow_compatible = False

    # Determine the type of file_obj
    if isinstance(file_obj, UploadedFile):
        file_type = "UploadedFile"
        file_bytesio = BytesIO(file_obj.getvalue())
    elif isinstance(file_obj, BytesIO):
        file_type = "BytesIO"
        file_bytesio = file_obj
    elif isinstance(file_obj, bytes):
        file_type = "bytes"
        file_bytesio = BytesIO(file_obj)
    else:
        return "UNKNOWN", "UNKNOWN", pillow_compatible

    # detect file format
    if is_pdf_file_format(file_bytesio):
        file_format = "PDF"
        pillow_compatible = True # its OK for later conversion
    else:
        # use pillow for image format detection
        file_bytesio.seek(0)
        try:
            with Image.open(file_bytesio) as img:
                file_format = img.format
                pillow_compatible = True
        except UnidentifiedImageError:
            file_format = imghdr.what(file_bytesio) or "UNKNOWN"
            # imghdr detected format, but its pillow incompatible
            pillow_compatible = False

    return file_format.upper(), file_type, pillow_compatible


def detect_file_format_and_compatibility(
        file_obj: Union[BytesIO, UploadedFile, bytes]
    ) -> Tuple[str, bool]:

    result = detect_file_attributes(file_obj)
    return result[0], result[2] # format, pillow_compatible


def detect_file_format_and_type(
        file_obj: Union[BytesIO, UploadedFile, bytes]
    ) -> Tuple[str, str]:

    result = detect_file_attributes(file_obj)
    return result[0], result[1] # format, type


def detect_file_format(
        file_obj: Union[BytesIO, UploadedFile, bytes]
    ) -> Tuple[str, str]:

    return detect_file_attributes(file_obj)[0] # format


def is_file_compatible(file_obj: UploadedFile) -> bool:
    return detect_file_attributes(file_obj)[2] # pillow_compatible
