import re

def validate_table_name(name: str):
    if name is not None and re.fullmatch('[a-zA-Z0-9_]+', name):
        return True
    return False
