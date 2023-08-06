from ayradb.core.manage_table.delete.response import DeleteTableResponse
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT

ACTION = "table_destroy"


def delete_table(table_name):
    query = {
        "action": ACTION,
        "table_name": table_name
    }
    delete_table_request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query)
    return RestManager().submit(delete_table_request, DeleteTableResponse.from_http_response)
