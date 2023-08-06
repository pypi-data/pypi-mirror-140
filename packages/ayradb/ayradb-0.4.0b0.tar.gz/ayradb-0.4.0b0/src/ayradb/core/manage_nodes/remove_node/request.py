from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT
from ayradb.core.manage_nodes.remove_node.response import RemoveNodeResponse
import json


def remove_node(name, ip):
    query = {
        "action": "remove_servers"
    }

    body = {
        "server_name": name,
        "server_ip_address": ip
    }

    request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query, body=json.dumps(body).encode('ascii'))
    return RestManager().submit(request, RemoveNodeResponse.from_http_response)
