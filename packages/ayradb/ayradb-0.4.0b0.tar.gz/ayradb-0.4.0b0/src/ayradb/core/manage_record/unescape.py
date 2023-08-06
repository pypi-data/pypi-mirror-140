ESCAPE_BYTE=b'\x5c'
DOUBLE_ESCAPE_BYTE=b'\x5c\x5c'

UNESCAPE_BYTE_DICT={
    0x7A: b'\x00', #null 	\z 0x5c 0x7a
    0x71: b'\x22', #" \q 0x5c 0x71 
    0x73: b'\x3B', #; \s 0x5c 0x73 
    0x5C: b'\x5C', #\ \\ 0x5c 0x5c
    0x6E: b'\x0A', #line-feed \n 0x5c 0x6e 
    0x66: b'\x0C', #form-feed \f 0x5c 0x66
    0x63: b'\x0D', #carriage-return \c 0x5c 0x63 
}

def unescape(string:bytes):
    str_len=string.__len__()
    idx=0
    splitted_response = string.split(DOUBLE_ESCAPE_BYTE)
    # Unescape splitted response [0]
    current_split=splitted_response[0].split(ESCAPE_BYTE)
    splitted_response[0]=current_split[0]
    for idx in range(1,current_split.__len__()):
        # For every sub array of splitted_response[0] splitted at \
        to_unescape = current_split[idx][0]
        unescaped_byte = UNESCAPE_BYTE_DICT.get(to_unescape)
        if unescaped_byte is None:
            # Error in escaping or unescaping (unexpected char)
            raise UnescapeException("Unescape char not found") 
        # Modify byte to unescape
        splitted_response[0]+=unescaped_byte+current_split[idx][1:]
    # Unescape splitted response [1:]
    for cursor in range(1,splitted_response.__len__()):
        # For each array splitted at \\
        current_split=splitted_response[cursor].split(ESCAPE_BYTE)
        splitted_response[cursor]=current_split[0]
        for idx in range(1,current_split.__len__()):
            # For each sub array splitted at \
            to_unescape = current_split[idx][0]
            unescaped_byte = UNESCAPE_BYTE_DICT.get(to_unescape)
            if unescaped_byte is None:
                # Error in escaping or unescaping (unexpected char)
                raise UnescapeException("Unescape char not found") 
            # Modify byte to unescape
            splitted_response[cursor]+=unescaped_byte+current_split[idx][1:]
        # Add unescaped slash (double slash in escaped version)
        splitted_response[0]+=b'\x5c'+splitted_response[cursor]
    return splitted_response[0]


# UNESCAPE_BYTE_DICT={
#     b'\x7A': b'\x00', #null 	\z 0x5c 0x7a
#     b'\x71': b'\x22', #" \q 0x5c 0x71 
#     b'\x73': b'\x3B', #; \s 0x5c 0x73 
#     b'\x5C': b'\x5C', #\ \\ 0x5c 0x5c
#     b'\x6E': b'\x0A', #line-feed \n 0x5c 0x6e 
#     b'\x66': b'\x0C', #form-feed \f 0x5c 0x66
#     b'\x63': b'\x0D', #carriage-return \c 0x5c 0x63 
# }
# def unescape(string:bytes):
#     str_len=string.__len__()
#     idx=0
#     escaped_field=bytearray() # Unescaped max size = escaped size
#     while idx<str_len:
#         curr_byte=string[idx:idx+1]
#         if curr_byte==ESCAPE_BYTE:
#             # Case UNESCAPE
#             # Check next byte
#             idx+=1
#             escape = UNESCAPE_BYTE_DICT.get(string[idx:idx+1])
#             if escape is None:
#                 # Error in escaping or unescaping (unexpected char)
#                 raise UnescapeException("Unescape char not found") 
#             escaped_field+=escape
#         else:
#             # Case DON'T unescape
#             escaped_field+=curr_byte
#         # Move to string next byte
#         idx+=1
#     return bytes(escaped_field)

# def unescape(string:bytes):
#     str_len=string.__len__()
#     idx=0
#     tot_size=0
#     escaped_field=bytearray(str_len) # Unescaped max size = escaped size
#     while idx<str_len:
#         curr_byte=string[idx:idx+1]
#         if curr_byte==ESCAPE_BYTE:
#             # Case UNESCAPE
#             # Check next byte
#             idx+=1
#             escape = UNESCAPE_BYTE_DICT.get(string[idx:idx+1])
#             if escape is None:
#                 # Error in escaping or unescaping (unexpected char)
#                 raise UnescapeException("Unescape char not found") 
#             escaped_field[tot_size:tot_size+1]=escape
#         else:
#             # Case DON'T unescape
#             escaped_field[tot_size]=string[idx]
#         # Move to string next byte
#         idx+=1
#         # Move to write next unescaped byte 
#         tot_size+=1
#     return bytes(escaped_field[0:tot_size])

class UnescapeException(BaseException):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message