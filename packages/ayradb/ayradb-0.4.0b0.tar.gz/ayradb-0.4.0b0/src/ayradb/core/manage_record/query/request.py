from ayradb.rest.http.request import Request
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.promise import Promise
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT
from ayradb.core.manage_record.query.response import QueryResponse

import json


def query_records(sql_query) -> Promise:
    # Create query
    query = {
        "action": "sqlq",
    }
    body = {
        "sql_query": sql_query,
    }
    query_request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query,
                            body=json.dumps(body).encode('ascii'))

    return RestManager().submit_to_long_queue(query_request, QueryResponse.from_http_response)

