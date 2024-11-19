import uuid

from typing import Literal


def generate_random_uuid(format: Literal["hex", "str"] = "hex") -> str:
    rand_uuid = uuid.uuid4()
    if format == "hex":
        return rand_uuid.hex
    elif format == "str":
        return str(rand_uuid)
    else:
        raise Exception(f'''
            format parameter must be "hex" or "str" 
            in generate_random_uuid()
                  
            ''')
