from ayradb.core.manage_record.check_existence.response import ContainsResponse
from ayradb.core.manage_record.format_key import format_key
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import TABLES_ENDPOINT


def check_record_existence(table_name, key):
    # Create query
    query = {
        "action": "table_read_row",
        "table_name": table_name,
        "key_column_name": "key_column",
        "key_value": format_key(key),
        "fields": "**"
    }
    contains_request = Request(Request.METHOD_GET, path=TABLES_ENDPOINT, query=query)
    return RestManager().submit(contains_request, ContainsResponse.from_http_response)