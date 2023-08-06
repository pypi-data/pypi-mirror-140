__all__ = ['CreateTableResponse', 'CreateTableError']

from ayradb.rest.http.response import Response
import re
from dataclasses import dataclass


class CreateTableError:
    # Request errors (local)
    FIELD_MAX_LENGTH_REQUIRED = -1  # Also managed remotely
    KEY_MAX_LENGTH_REQUIRED = -2  # Also managed remotely
    NOT_ENOUGH_NODES = -3
    # AyraDB errors
    ALREADY_EXISTS = 1
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "ERROR: [00019]:(00001): QFICRTAB_011: request json: table_description: table_conventional_name: the table already exists": CreateTableError.ALREADY_EXISTS,
    # Errors that should be verified also locally
    "ERROR: [00019]:(00001): CTDFJ_030.001: column_descriptions: column_max_net_length: not found": CreateTableError.FIELD_MAX_LENGTH_REQUIRED,
    "ERROR: [00019]:(00001): CTDFJ_030.002: column_descriptions: column_max_net_length: not a number": CreateTableError.KEY_MAX_LENGTH_REQUIRED,
    # Errors that shouldn't happen since they are internally managed
    "ERROR: [00016]:(00002): TFA_EEPA_018: endpoint action can't be done with this request method": CreateTableError.INTERNAL_ERROR,
}


@dataclass
class CreateTableResponse:

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
            return CreateTableResponse(True, 0)
        else:
            # Case error returned by ayra
            _error_msg = ""
            error = res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = CreateTableError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file

            return CreateTableResponse(False, error_code, _error_msg=_error_msg)
