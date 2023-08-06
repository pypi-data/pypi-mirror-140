__all__ = ['GetStructureResponse', 'GetStructureError']

from ayradb.rest.http.response import Response
import re
import json
from dataclasses import dataclass
from ayradb.core.manage_table.column import Column


class GetStructureError:
    # Request errors (local)
    INVALID_FIELD_NAME = -1
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "ERROR: [00005]:(00002): QFISGSPTRS_005: table not found":GetStructureError.TABLE_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "ERROR: [00016]:(00002): TFA_EEPA_018: endpoint action can't be done with this request method": GetStructureError.INTERNAL_ERROR,
    "ERROR: [00019]:(00001): TFA_EEPA_019.004: Too many parameters in the request uri": GetStructureError.INTERNAL_ERROR
}


@dataclass
class GetStructureResponse:

    success: bool
    error_code: int
    _error_msg: str
    structure: list

    def __init__(self, success, error_code,_error_msg="", description=None):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg
        self.structure = description

    @staticmethod
    def from_http_response(res: Response):
        error_code = 0
        _error_msg = ""
        fields = []
        if res.status_code == 200:
            success = True
            body = json.loads(res.body)
            body_description = body["column_descriptions"]
            for idx in range(0, body_description.__len__()):
                fields.append({Column.NAME: body_description[idx]["column_label"]})
                if "column_max_net_length" in body_description[idx] and body_description[idx]["column_max_net_length"] is not None:
                    fields[idx][Column.MAX_LENGTH] = body_description[idx]["column_max_net_length"] / 2  # FIXME: Remove /2 if escape factor is enabled
        else:
            # Case error returned by ayra
            success=False
            error=res.body.decode('ascii')
            # Search for server name inside error message
            match = re.search(r'^(([\s\S])+(?=(ERROR)))', error)
            if match is not None:
                # Case server name present in error
                error = error[match.end():]  # Remove server name from error
            internal_error = GetStructureError.INTERNAL_ERROR
            try:
                error_code = ERROR_DICT[error]
            except KeyError:
                error_code = internal_error
            if error_code == internal_error:
                _error_msg = error
                # TODO: save in a log file

        return GetStructureResponse(success,error_code,_error_msg=_error_msg, description=fields)
