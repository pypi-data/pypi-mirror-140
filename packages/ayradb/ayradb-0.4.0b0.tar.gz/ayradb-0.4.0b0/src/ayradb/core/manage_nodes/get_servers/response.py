__all__ = ['GetServersResponse', 'GetServersError']

from ayradb.rest.http.response import Response
import re
from dataclasses import dataclass


class GetServersError:
    # AyraDB errors
    INTERNAL_ERROR = 100


SEPARATOR = b'\x3b'
ERROR_DICT = {
    # Errors that shouldn't happen since they are internally managed
    "ERROR: [00016]:(00002): TFA_EEPA_018: endpoint action can't be done with this request method": GetServersError.INTERNAL_ERROR,
}


@dataclass
class GetServersResponse:

    success: bool
    servers: dict
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, servers=None, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self.servers = servers
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        if res.status_code == 200:
            servers = {}
            body: bytes = res.body
            splitted_body = body.split(SEPARATOR)
            # Parse body
            for cursor in range(0,splitted_body.__len__(),2):
                # splitted body is organized as [srv-name, srv-ip, srv-name, srv-ip,...]
                field_key = splitted_body[cursor]
                field_value = splitted_body[cursor+1]
                servers[field_key.decode('ascii')] = field_value.decode('ascii')
            return GetServersResponse(True, 0, servers=servers)
        else:
            # Case error returned by ayra
            _error_msg = ""
            error = res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = GetServersError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file
            return GetServersResponse(False, error_code, _error_msg=_error_msg)
