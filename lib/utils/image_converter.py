import base64
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
from pathlib import Path
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit import session_state as ss

from const.session_names import SessionNames as sn
from lib.utils.detect_file_attributes import detect_file_format_and_type


def read_image(path: Path) -> Image.Image:
    from lib.io.file_manager import FileManager
    fm = FileManager(crypt_key=ss[sn.ENCRYPT_KEY])
    return fm.read_invoice_image(path)


def base64encode(image: Path | Image.Image) -> str:
    if isinstance(image, Path):
        image = read_image(image)

    with BytesIO() as buffer:
        image.save(buffer, format='PNG')
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return base64_data


def prepare_base64_image(image: Path | Image.Image) -> str:
    return f"data:image/png;base64,{base64encode(image)}"


def uploaded_file_to_image(uploaded_file: UploadedFile) -> Image.Image:
    return Image.open(uploaded_file)


def merge_images_to_single_image(images: list[Image.Image]) -> Image.Image:
    # size of result image
    total_height = sum(image.height for image in images)
    max_width = max(image.width for image in images)

    # new image with size of result image
    combined_image = Image.new("RGB", (max_width, total_height))

    # merging images
    current_height = 0
    for image in images:
        combined_image.paste(image, (0, current_height))
        current_height += image.height

    return combined_image


def convert_pdf_to_images(pdf_file_in_bytes: bytes) -> list[Image.Image]:
    return convert_from_bytes(pdf_file_in_bytes)


def merge_mixed_files_to_single_image(
        files: list[UploadedFile | bytes]
    ) -> Image.Image:
    
    images_to_merge = []

    for file in files:
        file_format, file_type = detect_file_format_and_type(file)
        if file_type == "UploadedFile":
            file_in_bytes = file.read()
        else:
            file_in_bytes = file
        
        if file_format == 'PDF':
            pdf_images = convert_pdf_to_images(file_in_bytes)
            images_to_merge.extend(pdf_images)
        else:
            images_to_merge.append(Image.open(BytesIO(file_in_bytes)))

    result_image = merge_images_to_single_image(images_to_merge)

    return result_image


def resize_invoice_image(
        image: Image.Image,
        width: int | None = 800,
        height: int | None = None
) -> Image.Image:
    original_width, original_height = image.size

    if (original_width <= width):
        return image

    if width is not None and height is None:
        ratio = original_height / original_width
        height = int(width * ratio)
    elif height is not None and width is None:
        ratio = original_width / original_height
        width = int(height * ratio)
    elif width is None and height is None:
        width = 800
        ratio = original_height / original_width
        height = int(width * ratio)

    resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
    return resized_image
