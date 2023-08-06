from ayradb.rest.promise import Promise
from ayradb.rest.http.request import Request
from ayradb.rest.http.header import Header
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT
from ayradb.core.keep_alive.response import KeepAliveResponse


def generate_keep_alive_promise():
    query = {
        "action": "keep_alive"
    }

    headers = {
        Header.CONNECTION: "Keep-Alive"
    }

    req = Request(Request.METHOD_GET, path=SYSTEM_ENDPOINT, query=query, headers=headers)
    return Promise(req, KeepAliveResponse.from_http_response)
