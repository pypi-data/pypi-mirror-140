import json

from ayradb.core.manage_record.scan.actions import ACTION_SCAN_TABLE, SUB_ACTION_SCAN_START, SUB_ACTION_SCAN_CONTINUE
from ayradb.core.manage_record.scan.response_scan import ScanResponse, ScanError
from ayradb.core.validate import validate_field
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.rest.promise import Promise
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT


def scan(table_name, segment, fields=None, last_hash=None):
    # Create query
    query = {
        "action": ACTION_SCAN_TABLE,
    }
    # Create body common fields
    body = {
        "table_name": table_name,
        "subaction": SUB_ACTION_SCAN_CONTINUE,
        "last_key_hash": last_hash,
        "segment": str(segment),
    }
    if last_hash is None:
        # Less frequent (case scan start)
        body["subaction"] = SUB_ACTION_SCAN_START
        del body["last_key_hash"]
    if fields is None or fields.__len__() == 0:
        # Case scan all fields
        body["fields"] = "*"
    else:
        # Case scan only requested fields
        concat = fields[0]
        fields_valid = validate_field(concat)
        for fieldIdx in range(1, fields.__len__()):
            # Concat remaining fields
            curr_field = fields[fieldIdx]
            fields_valid = fields_valid and validate_field(curr_field)
            concat = f'{concat},{curr_field}'
        body["fields"] = concat

        if not fields_valid:
            # Case at least one invalid field
            return Promise.reject(ScanResponse(False, ScanError.INVALID_FIELD_NAME, None, None))

    # Case inserted fields are all valid or fields=="*"
    scan_start_request = \
        Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query, body=json.dumps(body).encode('ascii'))
    return RestManager().submit(scan_start_request, ScanResponse.from_http_response)
