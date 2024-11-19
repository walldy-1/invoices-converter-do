from datetime import datetime
from streamlit.runtime.uploaded_file_manager import UploadedFile

from const.invoice import InvoiceDateFormats
from lib.utils.detect_file_attributes import is_file_compatible


def validate_uploaded_files(files: list[UploadedFile]) -> str:
    err_message = ""

    for file in files:
        if not is_file_compatible(file):
            err_message += f'Plik {file.name} ma nieprawidłowy format lub jest uszkodzony\n'
    
    return err_message if err_message else "OK"


def validate_date(date_str: str, db_format_only: bool = False) -> bool:
    if not date_str:
        return True

    if db_format_only:
        allowed_formats = [InvoiceDateFormats.DB_FORMAT]
    else:
        allowed_formats = InvoiceDateFormats.ALLOWED_FORMATS

    for frmt in allowed_formats:
        try:
            datetime.strptime(date_str, frmt)
            return True
        except ValueError:
            continue

    return False


def convert_date_to_db_format(date_str: str) -> str:
    if not date_str:
        return None

    for frmt in InvoiceDateFormats.ALLOWED_FORMATS:
        try:
            date_obj = datetime.strptime(date_str, frmt)
            return date_obj.strftime(InvoiceDateFormats.DB_FORMAT)
        except ValueError:
            continue

    raise ValueError("Nieprawidłowy format daty")


def to_float(float_str: str) -> float | None:
    if not float_str:
        return None

    try:
        return float(str(float_str).replace(",", "."))
    except ValueError:
        return "Nieprawidłowy zapis liczby"


def try_fix_amount(amount_str: str) -> str:
    return str(amount_str).replace(" ", "").replace('.', ',')
    

def validate_amount(amount_str: str) -> bool:
    try:
        float(str(amount_str).replace(",", "."))
        return True
    except ValueError:
        return False
    

def extract_digits(string: str) -> str:
    return "".join(filter(str.isdigit, string))


def try_fix_nip(nip_str: str) -> str:
    return extract_digits(nip_str)


def validate_nip(nip_str: str) -> bool:
    if not nip_str.isdigit():
        return False

    if len(nip_str) != 10:
        return False
    
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    sum = 0
    for i in range(9):
        sum += int(nip_str[i]) * weights[i]
    
    rest = sum % 11
    control_digit = int(nip_str[9])

    return rest == control_digit
