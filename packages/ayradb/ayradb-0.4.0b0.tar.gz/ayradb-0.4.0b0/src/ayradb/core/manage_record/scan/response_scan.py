__all__ = ['ScanResponse', 'ScanError']

from ayradb.rest.http.response import Response
from ayradb.core.manage_record.unescape import *
import re
from dataclasses import dataclass

SEPARATOR = b'\x3b'
LAST_HASH_KEY_NAME = b'__scan_table__last_key_hash__'
KEY_COLUMN_NAME = b'key_column'


class ScanError:
    # Request errors (local)
    INVALID_FIELD_NAME=-1
    # AyraDB errors
    TABLE_NOT_FOUND=1
    SEGMENT_END=2
    INVALID_SEGMENT = 3
    SEGMENT_OUT_OF_RANGE = 4
    INTERNAL_ERROR=100


ERROR_DICT = {
    "ERROR: [00405]:(00008): TFA_EEPA_019: No parameter group found implementing the requested action: probably action group value":ScanError.TABLE_NOT_FOUND,
    "ERROR: [00002]:(00002): TFDRC_002.003: scan_table: no next keys found": ScanError.SEGMENT_END,
    "ERROR: [00019]:(00001): TFA_MTKOSCANTABLE_012: message_reference->body: segment: not a number": ScanError.INVALID_SEGMENT,
    "ERROR: [00019]:(00001): TFA_MTKOSCANTABLE_013: message_reference->body: segment: out of range": ScanError.SEGMENT_OUT_OF_RANGE,
    # Errors that shouldn't happen since they are internally managed
    "ERROR: [00016]:(00002): TFA_EEPA_018: endpoint action can't be done with this request method": ScanError.INTERNAL_ERROR,
}


@dataclass
class ScanResponse:

    success: bool
    content: dict
    last_hash: str
    key_column: str
    segment_ended: bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, last_hash, key_column, segment_end=False, content=None, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self.last_hash = last_hash
        self.key_column = key_column
        self.segment_ended = segment_end
        self.content = content
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        error_code = 0
        _error_msg = ""
        last_hash = ""
        key_column = ""
        content = {}
        if res.status_code == 200:
            success = True
            try:
                body: bytes = res.body
                splitted_body = body.split(SEPARATOR)
                # Parse body
                for cursor in range(0, splitted_body .__len__(),2):
                    # splitted body is organized as [key, value, key, value,...]
                    field_key = splitted_body[cursor]
                    field_value = unescape(splitted_body[cursor+1])
                    if field_key == LAST_HASH_KEY_NAME:
                        # Case last key hash found
                        last_hash = field_value.decode('ascii')
                    elif field_key == KEY_COLUMN_NAME:
                        # Case key column field found
                        key_column = field_value.decode('ascii')
                    else:
                        # Case record field found
                        field_value = unescape(field_value)
                        content[field_key.decode('utf-8')] = field_value

            except UnescapeException:
                success = False
                error_code = ScanError.INTERNAL_ERROR
                _error_msg = "Parsing error"
        else:
            # Case error returned by ayra
            success = False
            error = res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = ScanError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file
        return ScanResponse(success, error_code, last_hash, key_column, content=content, _error_msg=_error_msg)
