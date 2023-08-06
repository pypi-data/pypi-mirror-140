__all__ = ['AddNodeResponse', 'AddNodeError']

from ayradb.rest.http.response import Response
import re
from dataclasses import dataclass


class AddNodeError:
    INTERNAL_ERROR = 100

ERROR_DICT = {

}

@dataclass
class AddNodeResponse:
    success: bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        success = True
        error_code = 0
        _error_msg = ""
        if res.status_code == 200:
            success = True
        else:
            # Case error returned by ayra
            success = False
            error = res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = AddNodeError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file

        return AddNodeResponse(success, error_code, _error_msg=_error_msg)


