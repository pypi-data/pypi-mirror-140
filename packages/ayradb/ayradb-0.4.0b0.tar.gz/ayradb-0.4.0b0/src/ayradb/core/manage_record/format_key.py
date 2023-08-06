def format_key(key: str):
    return ''.join([char.encode('utf-8').hex() for char in key])