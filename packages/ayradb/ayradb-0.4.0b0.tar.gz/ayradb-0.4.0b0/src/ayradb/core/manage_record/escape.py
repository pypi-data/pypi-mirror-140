import re

ESCAPE_DICT = {
    b'\x00': rb'\z',    # null        -> \z 0x5c 0x7a
    b'"': rb'\q',       # "           -> \q 0x5c 0x71
    b';': rb'\s',       # ;           -> \s 0x5c 0x73
    b'\\': rb'\\',      # \           -> \\ 0x5c 0x5c
    b'\n': rb'\n',      # line-feed   -> \n 0x5c 0x6e
    b'\f': rb'\f',      # form-feed   -> \f 0x5c 0x66
    b'\r': rb'\c',      # carr-return -> \c 0x5c 0x63
}

ESCAPE_CLASS = '[' + ''.join(r'\x' + x.hex() for x in ESCAPE_DICT) + ']'
ESCAPE_REGEX = re.compile(ESCAPE_CLASS.encode())


def escape(string: bytes) -> bytes:
    return re.sub(ESCAPE_REGEX, lambda m: ESCAPE_DICT[m.group(0)], string)

# ESCAPE_DICT={
#     0x00: [0x5C,0x7A], # null        -> \z 0x5c 0x7a
# 	0x22: [0x5C,0x71], # "           -> \q 0x5c 0x71
# 	0x3B: [0x5C,0x73], # ;           -> \s 0x5c 0x73
# 	0x5C: [0x5C,0x5C], # \           -> \\ 0x5c 0x5c
# 	0x0A: [0x5C,0x6E], # line-feed   -> \n 0x5c 0x6e
# 	0x0C: [0x5C,0x66], # form-feed   -> \f 0x5c 0x66
# 	0x0D: [0x5C,0x63], # carr-return -> \c 0x5c 0x63
# }

# def escape(string: bytes):
#     str_len=string.__len__()
#     escaped_array=[]
#     for i in range(0,str_len):
#         curr_byte=string[i]
#         escape = ESCAPE_DICT.get(curr_byte)
#         if escape is None:
#             # Don't escape current byte
#             escaped_array.append(curr_byte)
#         else:
#             # Escape current byte
#             escaped_array.extend(escape)
#     return bytes(escaped_array)

# def escape(string: bytes):
#     str_len=string.__len__()
#     #Escaped max size is twice unescaped size
#     escaped_array=bytearray(2*str_len)
#     total_size=0
#     for i in range(0,str_len):
#         curr_byte=string[i:i+1]
#         escape = ESCAPE_DICT.get(curr_byte)
#         if escape is None:
#             # Don't escape current byte
#             escaped_array[total_size:total_size+1]=curr_byte
#             total_size+=1
#         else:
#             # Escape current byte
#             escaped_array[total_size:total_size+2]=escape
#             total_size+=2
#     return bytes(escaped_array[0:total_size])
