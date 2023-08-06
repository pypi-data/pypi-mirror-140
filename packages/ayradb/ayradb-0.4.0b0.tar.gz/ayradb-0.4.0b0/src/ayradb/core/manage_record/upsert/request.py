from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.rest.promise import Promise
from ayradb.core.endpoints.endpoints import TABLES_ENDPOINT
from ayradb.core.manage_record.format_key import format_key
from ayradb.core.manage_record.escape import escape
from ayradb.core.manage_record.upsert.response import UpsertResponse, UpsertError
from ayradb.core.validate import validate_field

FIELD_VALUE_SEPARATOR = b';'
FIELD_KEY_SEPARATOR = ","


def upsert_record(table_name: str, key: str, fields: dict) -> Promise:
    # Create query
    query = {
        "action": "table_insert_row",
        "table_name": table_name,
        "key_column_name": "key_column",
        "key_value": format_key(key), # Key is escaped
        "imode":"drop_older_record_with_same_key"
    }
    are_fields_valid = True
    query_fields = ""
    body = bytearray()
    first_el = True
    for field_key, field_value in fields.items():
        # Generate body and fields query argument
        are_fields_valid = are_fields_valid and validate_field(field_key)
        if first_el:
            body += escape(field_value)
            query_fields = field_key
            first_el = False
        else:
            body += FIELD_VALUE_SEPARATOR+escape(field_value)
            query_fields = f'{query_fields}{FIELD_KEY_SEPARATOR}{field_key}'
    if not are_fields_valid:
        return Promise.reject(UpsertResponse(False,UpsertError.INVALID_FIELD_NAME))
    query["fields"] = query_fields
    upsert_request = Request(Request.METHOD_PUT, path=TABLES_ENDPOINT, query=query, body=body)
    return RestManager().submit(upsert_request, UpsertResponse.from_http_response)
