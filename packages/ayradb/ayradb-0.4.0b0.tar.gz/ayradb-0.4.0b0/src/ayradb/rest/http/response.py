from dataclasses import dataclass
from ayradb.rest.http.header import Header


@dataclass
class Response:
    status_code: int
    status_message: str
    headers: dict
    body: bytes
    chunked: bool
    last_chunk: bool

    # Position trackers
    header_buffer_seek_pos: int
    body_parsing_start_pos: int

    # Parsing flags
    flag_proto_ok: bool
    flag_status_code_ok: bool
    flag_status_msg_ok: bool
    flag_headers_ok: bool
    __flag_body_ok: bool

    _HTTP_PROTO_BYTES_SIZE = 8
    _HTTP_STATUS_CODE_FIRST_BYTE_IDX = 9
    _HTTP_STATUS_MSG_FIRST_BYTE_IDX = 13
    _HTTP_FIRST_LINE_SIZE = 14
    _HTTP_LINE_TERMINATOR = b'\x0d\x0a'

    _HTTP_STATUS_DICT = {
        # 1xx INFORMATIONAL
        b'\x31\x30\x30': 100,  # 100 - Continue
        b'\x31\x30\x31': 101,  # 101 - Switching protocols
        b'\x31\x30\x32': 102,  # 102 - Processing
        b'\x31\x30\x33': 103,  # 103 - Early hints
        b'\x31\x39\x38': 198,  # 198 - Cherrydata-provisional-update-servers-coord
        # 2xx SUCCESS
        b'\x32\x30\x30': 200,  # 200 - OK
        b'\x32\x30\x31': 201,  # 201 - Created
        b'\x32\x30\x32': 202,  # 202 - Accepted
        b'\x32\x30\x33': 203,  # 203 - Non-Authoritative Information
        b'\x32\x30\x34': 204,  # 204 - No Content
        b'\x32\x30\x35': 205,  # 205 - Reset Content
        b'\x32\x30\x36': 206,  # 206 - Partial Content
        b'\x32\x30\x37': 207,  # 207 - Multi status
        # 3xx REDIRECT
        # TODO: add missing
        b'\x33\x30\x30': 300,  # 300 - Multiple choices
        b'\x33\x30\x31': 301,  # 301 - Moved permanently
        # 4xx CLIENT ERRORs
        b'\x34\x30\x30': 400,  # 400 - Bad request
        b'\x34\x30\x31': 401,  # 401 - Unauthorized
        b'\x34\x30\x32': 402,  # 402 - Payment required
        b'\x34\x30\x33': 403,  # 403 - Forbidden
        b'\x34\x30\x34': 404,  # 404 - Not found
        b'\x34\x30\x35': 405,  # 405 - Method not allowed
        # 5xx CLIENT ERRORs
        b'\x35\x30\x30': 500,  # 500 - Internal Server Error
        b'\x35\x30\x31': 501,  # 501 - Not Implemented
        b'\x35\x30\x32': 502,  # 502 - Bad Gateway
        b'\x35\x30\x33': 503,  # 503 - Service Unavailable
        b'\x35\x30\x34': 504,  # 504 - Gateway Timeout
        b'\x35\x30\x35': 505,  # 505 - HTTP Version Not Supported
    }

    def __init__(self):
        self.flag_proto_ok = False
        self.flag_status_code_ok = False
        self.flag_status_msg_ok = False
        self.flag_headers_ok = False
        self.__flag_body_ok = False
        self.header_buffer_seek_pos = 0
        self.body_parsing_start_pos = 0
        self.headers = {}
        self.body = b''
        self.chunked = False
        self.last_chunk = False

    def from_byte_array(self, byte_array):
        if not self.flag_proto_ok:
            # HTTP proto still not parsed
            if byte_array.__len__() < Response._HTTP_PROTO_BYTES_SIZE:
                # Not enough bytes to check protocol
                return 0
            else:
                # Verify that in first 8 bytes there is HTTP/1.1
                self.flag_proto_ok = byte_array[
                                     0:Response._HTTP_PROTO_BYTES_SIZE] == b'\x48\x54\x54\x50\x2F\x31\x2e\x31'
                if not self.flag_proto_ok:
                    # Malformed message: HTTP/1.1 isn't in first 8 bytes
                    return -1

        if not self.flag_status_code_ok:
            # Status code not parsed

            # Status code still not parsed
            if byte_array.__len__() < Response._HTTP_FIRST_LINE_SIZE:
                # Not enough bytes to check status
                return 0
            # Check that a space is present after HTTP/1.1
            if byte_array[Response._HTTP_PROTO_BYTES_SIZE] != 0x20:
                # Case space not present (malformed message)
                return -1
            # Check http status code
            status_bytes = byte_array[
                           Response._HTTP_STATUS_CODE_FIRST_BYTE_IDX:Response._HTTP_STATUS_CODE_FIRST_BYTE_IDX + 3]
            self.status_code = Response._HTTP_STATUS_DICT.get(status_bytes)
            if self.status_code is None:
                # Bytes didn't correspond to a valid HTTP status
                return -1
            # Check that a space is present after the status
            if byte_array[Response._HTTP_STATUS_CODE_FIRST_BYTE_IDX + 3] != 0x20:
                # Space not present (malformed message)
                return -1
            # Status code parsed correctly
            self.flag_status_code_ok = True

        if not self.flag_status_msg_ok:
            # Status message not parsed

            # Start parsing from status message first byte position
            status_msg_pos = Response._HTTP_STATUS_MSG_FIRST_BYTE_IDX
            # Seek next \r\n
            next_rn_position = Response._seek_line_terminator(byte_array, start=status_msg_pos)
            if next_rn_position == -1:
                # \r\n not found (not enough bytes)
                return 0
            else:
                self.flag_status_msg_ok = True
                # Decode status msg
                self.status_message = byte_array[status_msg_pos:next_rn_position] \
                    .decode('utf8')
                # Start searching for the headers from the first byte
                # after the line terminator
                self.header_buffer_seek_pos = next_rn_position + Response._HTTP_LINE_TERMINATOR.__len__()

        while not self.flag_headers_ok:
            # Header still not parsed

            # Seek next \r\n starting from the first not parsed
            # byte of the headers
            next_rn_position = Response._seek_line_terminator(byte_array, start=self.header_buffer_seek_pos)
            if next_rn_position == -1:
                # \r\n not found (not enough bytes)
                return 0
            if next_rn_position == self.header_buffer_seek_pos:
                # This \r\n is preceded by another \r\n
                # Double line terminator means headers end
                # Since a HTTP message has at least 1 header (Content-Length)
                # we can skip the case with 0 headers
                self.flag_headers_ok = True
                self.body_parsing_start_pos = self.header_buffer_seek_pos + Response._HTTP_LINE_TERMINATOR.__len__()
                break
            # Decode header row
            header_row = byte_array[self.header_buffer_seek_pos:next_rn_position] \
                .decode('utf8')
            # Split header in key value
            splitted_header = header_row.split(':')
            if splitted_header[1][0] == ' ':
                # Remove whitespace before adding key value pair to headers
                self.headers[splitted_header[0]] = splitted_header[1][1:]
            else:
                # Add key value pair to headers
                self.headers[splitted_header[0]] = splitted_header[1]
            # Move header start position after \r\n
            self.header_buffer_seek_pos = next_rn_position + Response._HTTP_LINE_TERMINATOR.__len__()

        if self.headers.get(Header.TRANSFER_ENCODING) == 'chunked':
            self.chunked = True
            while not self.__flag_body_ok:
                next_rn_position = Response._seek_line_terminator(byte_array, start=self.body_parsing_start_pos)
                if next_rn_position == -1:
                    # \r\n not found (not enough bytes)
                    return 0
                chunk_start_pos = next_rn_position + Response._HTTP_LINE_TERMINATOR.__len__()
                if next_rn_position == self.body_parsing_start_pos:
                    # Case end of message (but not last chunk)
                    self.__flag_body_ok = True
                    self.body_parsing_start_pos += Response._HTTP_LINE_TERMINATOR.__len__()
                else:
                    # Retrieve chunk length and convert it to int
                    chunk_length = Response.__retrieve_chunk_length(byte_array, self.body_parsing_start_pos,
                                                                    next_rn_position)
                    if chunk_length == 0:
                        self.last_chunk = True
                        self.__flag_body_ok = True
                    else:
                        self.body += (byte_array[chunk_start_pos:chunk_start_pos + chunk_length])
                    # Update parsing start position for next iteration
                    self.body_parsing_start_pos = chunk_start_pos + chunk_length + Response._HTTP_LINE_TERMINATOR.__len__()
                    # Extract the record
            return self.body_parsing_start_pos

        else:
            # Get message length
            content_length = int(self.headers.get(Header.CONTENT_LENGTH))
            missing_bytes = content_length - self.body.__len__()
            parsable_bytes = 0
            if byte_array.__len__() < self.body_parsing_start_pos + missing_bytes:
                # Case not enough bytes to parse the whole body
                # Parse all the available bytes
                parsable_bytes = byte_array.__len__() - self.body_parsing_start_pos
            else:
                parsable_bytes = missing_bytes
            self.body += byte_array[self.body_parsing_start_pos:self.body_parsing_start_pos + parsable_bytes]
            self.body_parsing_start_pos = self.body_parsing_start_pos + parsable_bytes
            if self.body.__len__() != content_length:
                # Missing bytes from body
                return 0
            else:
                return self.body_parsing_start_pos

    @staticmethod
    def __retrieve_chunk_length(byte_array, start, end):
        # Retrieve chunk length and convert it to int
        chunk_length = byte_array[start:end].decode('ascii')
        return int(chunk_length, 16)  # The length is in HEX notation, that is why we insert 16.

    @staticmethod
    def _seek_line_terminator(byte_array, start=0):
        return Response._seek_sub_slice(byte_array, Response._HTTP_LINE_TERMINATOR, start=start)

    @staticmethod
    def _seek_sub_slice(byte_array, sub_slice, start=0):
        # Start searching from the start position
        idx = start
        sub_sl_len = sub_slice.__len__()
        # Search up for the first sub slice byte 
        # up to (byte_array.length - sub_slice.length) byte
        # After that we don't have enough byte to find the pattern
        while idx + sub_sl_len - 1 < byte_array.__len__():
            if byte_array[idx] == sub_slice[0]:
                # First byte of the pattern found
                idx += 1
                # Move to next and check remaining bytes
                if byte_array[idx:idx + sub_sl_len - 1] == sub_slice[1:]:
                    # Pattern found (Move back to original position)
                    return idx - 1
            else:
                idx += 1
        # Pattern not found
        return -1
