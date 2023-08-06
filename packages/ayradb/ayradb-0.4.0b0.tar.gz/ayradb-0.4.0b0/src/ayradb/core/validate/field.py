import re

def validate_field(field: str):
    if field is not None and re.fullmatch('[a-zA-Z0-9_.-]+', field):
        return True
    return False