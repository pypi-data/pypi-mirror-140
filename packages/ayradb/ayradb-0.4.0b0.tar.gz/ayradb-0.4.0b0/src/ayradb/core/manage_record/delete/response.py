__all__ = ['DeleteResponse', 'DeleteError']

from ayradb.rest.http.response import Response
import re
from dataclasses import dataclass


class DeleteError:
    # Request errors (local)
    INVALID_FIELD_NAME=-1
    # AyraDB errors
    TABLE_NOT_FOUND=1
    FIELD_NOT_FOUND=2
    INTERNAL_ERROR=100


ERROR_DICT = {
    "ERROR: [00405]:(00008): TFA_EEPA_019: No parameter group found implementing the requested action: probably action group value":DeleteError.TABLE_NOT_FOUND,
    "ERROR: [00017]:(00001): TFA_MDAI_016.003: the specified field does not exist": DeleteError.FIELD_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "ERROR: [00016]:(00002): TFA_EEPA_018: endpoint action can't be done with this request method": DeleteError.INTERNAL_ERROR,
}


@dataclass
class DeleteResponse:

    success : bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code,_error_msg=""):
        self.success=success
        self.error_code=error_code
        self._error_msg=_error_msg

    @staticmethod
    def from_http_response(res: Response):
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
                error=error[match.end():]  # Remove server name from error
            internal_error=DeleteError.INTERNAL_ERROR
            try:
                error_code=ERROR_DICT[error]
            except KeyError:
                error_code=internal_error
            if error_code == internal_error:
                _error_msg=error
                # TODO: save in a log file

        return DeleteResponse(success, error_code, _error_msg=_error_msg)
