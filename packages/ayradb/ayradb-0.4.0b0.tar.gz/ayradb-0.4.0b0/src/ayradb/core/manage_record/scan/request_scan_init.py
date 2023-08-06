import json

from ayradb.core.manage_record.scan.actions import ACTION_SCAN_TABLE, SUB_ACTION_SCAN_INIT
from ayradb.core.manage_record.scan.response_scan_init import ScanInitResponse
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT


def scan_init(table_name):
    # Create query
    query = {
        "action": ACTION_SCAN_TABLE,
    }
    # Create body
    body = {
        "table_name": table_name,
        "subaction": SUB_ACTION_SCAN_INIT
    }

    json_body = json.dumps(body).encode('ascii')
    scan_init_request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query, body=json_body)
    return RestManager().submit(scan_init_request, ScanInitResponse.from_http_response)