import json

from ayradb.core.manage_table.get_structure.response import GetStructureResponse
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT

QUERY_ACTION = "set_get_system_parameter"
BODY_ACTION = "get"


def get_table_structure(table_name):
    query = {
        "action": QUERY_ACTION,
    }
    body = {
        "action": BODY_ACTION,
        "target_parameter": "table_record_structure",
        "table_name": table_name
    }

    get_table_request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query, body=json.dumps(body).encode('ascii'))
    return RestManager().submit(get_table_request, GetStructureResponse.from_http_response)
