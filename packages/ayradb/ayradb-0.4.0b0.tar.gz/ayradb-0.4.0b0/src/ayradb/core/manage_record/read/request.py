from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.rest.promise import Promise
from ayradb.core.endpoints.endpoints import TABLES_ENDPOINT
from ayradb.core.manage_record.format_key import format_key
from ayradb.core.manage_record.read.response import ReadResponse, ReadError
from ayradb.core.validate import validate_field


def read_record(table_name, key, fields=None):
    # Create query
    query = {
        "action": "table_read_row",
        "table_name": table_name,
        "key_column_name": "key_column",
        "key_value": format_key(key),   # Key is escaped
    }
    if fields is None or fields.__len__() == 0:
        # Case read all fields
        query["fields"] = "*"
        # Build request
        read_request = Request(Request.METHOD_GET, path=TABLES_ENDPOINT, query=query)
        # Submit request to rest manager
        return RestManager().submit(read_request, ReadResponse.from_http_response)
    else:
        # Case read only specific fields
        concat = fields[0]
        fields_valid = validate_field(concat)
        for fieldIdx in range(1, fields.__len__()):
            # Concat remaining fields
            curr_field = fields[fieldIdx]
            fields_valid = fields_valid and validate_field(curr_field)
            concat = f'{concat},{curr_field}'
        query["fields"] = concat

        # To reduce number of controls [and faster than if] for valid 
        # queries (most times) we control validity only once after 
        # concatenating fields
        if fields_valid:
            # All fields ok
            # Build request
            read_request = Request(Request.METHOD_GET, path=TABLES_ENDPOINT, query=query)
            # Submit request to rest manager
            return RestManager().submit(read_request, ReadResponse.from_http_response)
        else:
            # At least one invalid field
            return Promise.reject(ReadResponse(False, ReadError.INVALID_FIELD_NAME))  # Solved promise with error