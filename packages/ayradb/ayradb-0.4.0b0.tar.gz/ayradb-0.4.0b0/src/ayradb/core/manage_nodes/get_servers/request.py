from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT
from ayradb.core.manage_nodes.get_servers.response import GetServersResponse
import json


def get_servers():
    query = {
        "action": "set_get_system_parameter"
    }

    body = {
        "target_parameter": "servers_coordinates", 
        "action": "get"
    }

    request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query, body=json.dumps(body).encode('ascii'))
    return RestManager().submit(request, GetServersResponse.from_http_response)