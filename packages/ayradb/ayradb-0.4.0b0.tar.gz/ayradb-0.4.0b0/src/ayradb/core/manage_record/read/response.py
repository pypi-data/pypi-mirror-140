__all__ = ['ReadResponse', 'ReadError']

from ayradb.rest.http.response import Response
from ayradb.core.manage_record.unescape import *
import re
from dataclasses import dataclass

UNESCAPE_ERR_MSG = "Error during unescaping"
SEPARATOR = b'\x3b'


class ReadError:
    # Request errors (local)
    INVALID_FIELD_NAME = -1
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    RECORD_NOT_FOUND = 2
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "ERROR: [00405]:(00008): TFA_EEPA_019: No parameter group found implementing the requested action: probably action group value":ReadError.TABLE_NOT_FOUND,
    "ERROR: [00002]:(00002): TFDRC_007: No data found for this search": ReadError.RECORD_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "ERROR: [00016]:(00002): TFA_EEPA_018: endpoint action can't be done with this request method": ReadError.INTERNAL_ERROR,
}


@dataclass
class ReadResponse:

    success: bool
    content: dict
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, content=None, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self.content = content
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        error_code = 0
        _error_msg = ""
        content = {}
        if res.status_code == 200:
            success = True
            try:
                body: bytes = res.body
                splitted_body = body.split(SEPARATOR)
                # Parse body
                for cursor in range(0, splitted_body.__len__(), 2):
                    # splitted body is organized as [key, value, key, value,...]
                    field_key = splitted_body[cursor]
                    field_value = unescape(splitted_body[cursor+1])
                    content[field_key.decode('utf-8')] = field_value

            except UnescapeException:
                success = False
                error_code = ReadError.INTERNAL_ERROR
                _error_msg = UNESCAPE_ERR_MSG
        else:
            # Case error returned by ayra
            success = False
            error = res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = ReadError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file
        return ReadResponse(success, error_code, content=content, _error_msg=_error_msg)