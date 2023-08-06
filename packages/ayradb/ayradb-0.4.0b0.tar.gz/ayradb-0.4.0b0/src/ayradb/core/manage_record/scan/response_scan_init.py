__all__ = ['ScanInitResponse', 'ScanInitError']

from ayradb.rest.http.response import Response
import re
from dataclasses import dataclass
import json


class ScanInitError:
    # Request errors (local)
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "ERROR: TFA_MTKO_015: trans_h__manage_transaction_kick_off__scan_table:ERROR: [00005]:(00002): TFA_MTKOSCANTABLE_008: table not found": ScanInitError.TABLE_NOT_FOUND,
    "ERROR: [00005]:(00002): TFA_MTKOSCANTABLE_008: table not found": ScanInitError.TABLE_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "ERROR: [00016]:(00002): TFA_EEPA_018: endpoint action can't be done with this request method": ScanInitError.INTERNAL_ERROR,
    "ERROR: TFA_MTKO_015: trans_h__manage_transaction_kick_off__scan_table:ERROR: [00019]:(00001): TFA_MTKOSCANTABLE_008: message_reference->body: subaction: wrong value": ScanInitError.INTERNAL_ERROR,
}


@dataclass
class ScanInitResponse:

    success: bool
    error_code: int
    _error_msg: str
    segments: int

    def __init__(self, success, error_code, n_segments=0, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self.segments = n_segments
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        if res.status_code == 200:
            body=json.loads(res.body)
            return ScanInitResponse(True, 0, n_segments=body["n_segments"])
        else:
            # Case error returned by ayra
            _error_msg = ""
            error = res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = ScanInitError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file
            return ScanInitResponse(False,error_code,_error_msg=_error_msg)