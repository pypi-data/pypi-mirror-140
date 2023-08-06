from ayradb.core.manage_table.truncate.response import TruncateTableResponse
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT

ACTION = "table_truncate"

def truncate_table(table_name):
    query = {
        "action": ACTION,
        "table_name": table_name
    }

    truncate_table_request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query)
    return RestManager().submit(truncate_table_request, TruncateTableResponse.from_http_response)
