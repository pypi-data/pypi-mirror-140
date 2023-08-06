from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.rest.promise import Promise
from ayradb.core.endpoints.endpoints import TABLES_ENDPOINT
from ayradb.core.manage_record.format_key import format_key
from ayradb.core.manage_record.delete.response import DeleteResponse, DeleteError
from ayradb.core.validate import validate_field


def delete_record(table_name, key, fields=None):
    # Create query
    query = {
        "action": "table_delete_row",
        "table_name": table_name,
        "key_column_name": "key_column",
        "key_value": format_key(key),  # Key is escaped
    }
    are_fields_valid = True
    if fields is not None and fields.__len__() > 0:
        # Case delete only specific fields [NO_SQL table only]
        concat = fields[0]
        fields_valid = validate_field(concat)
        for fieldIdx in range(1, fields.__len__()):
            # Concat remaining fields
            curr_field = fields[fieldIdx]
            fields_valid = fields_valid and validate_field(curr_field)
            concat = f'{concat},{curr_field}'
        query["fields"] = concat
    if not are_fields_valid:
        return Promise.reject(DeleteResponse(False, DeleteError.INVALID_FIELD_NAME))
    delete_request = Request(Request.METHOD_DELETE, path=TABLES_ENDPOINT, query=query)
    return RestManager().submit(delete_request, DeleteResponse.from_http_response)
