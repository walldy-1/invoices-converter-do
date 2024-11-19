import json


# recursive iterations for all levels of template
# template can contain lists, dicts and simple values
def convert_template_structure(template, clear_values):
    if isinstance(template, dict):
        return {key: convert_template_structure(value, clear_values) for key, value in template.items()}
    elif isinstance(template, list):
        return [convert_template_structure(item, clear_values) for item in template]
    else:
        return None if clear_values else template


def template_to_str(template, clear_values: bool = False) -> str:
    converted_template = convert_template_structure(template, clear_values)
    structure = json.dumps(converted_template, ensure_ascii=False, indent=4)
    return structure