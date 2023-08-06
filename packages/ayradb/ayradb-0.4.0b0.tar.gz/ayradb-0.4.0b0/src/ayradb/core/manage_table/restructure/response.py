__all__ = ['RestructureTableResponse', 'RestructureTableError']

from ayradb.rest.http.response import Response
import re
from dataclasses import dataclass


class RestructureTableError:    # TODO
    # Request errors (local)
    FIELD_MAX_LENGTH_REQUIRED = -1  # Also managed remotely
    KEY_MAX_LENGTH_REQUIRED = -2  # Also managed remotely
    NOT_ENOUGH_NODES = -3
    # AyraDB errors
    INTERNAL_ERROR = 100

ERROR_DICT = {

}


@dataclass
class RestructureTableResponse:

    success: bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code,_error_msg=""):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        if res.status_code == 200:
            return RestructureTableResponse(True, 0)
        else:
            # Case error returned by ayra
            _error_msg = ""
            error = res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = RestructureTableError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file

            return RestructureTableResponse(False, error_code, _error_msg=_error_msg)
