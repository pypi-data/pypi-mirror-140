from ayradb.core.manage_table.create_lists import create_server_list_from_dict, create_column_list
from ayradb.rest.promise import Promise
from ayradb.core.manage_table.create.response import CreateTableResponse, CreateTableError
from ayradb.core.manage_table.column import COLUMN_MAX_LENGTH, COLUMN_NAME_KEY
from ayradb.core.manage_table.types import TABLE_FIXED_LENGTH
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT, TABLES_ENDPOINT
import json

ACTION_TABLE_CREATE = "table_create"
USER_TABLE = "user_table"
MINIMUM_REPLICATION = 1
DEFAULT_ESCAPE_FACTOR = 1  # 100%


def create_table(name, fill_type, user_columns:[], servers:dict, replication=1, table_max_size=1, tablet_max_size=1, key_max_size =-1, escape_factor=DEFAULT_ESCAPE_FACTOR):
    # Validate received fields:
    if replication > MINIMUM_REPLICATION > servers.__len__():
        return Promise.reject(CreateTableResponse(False,CreateTableError.NOT_ENOUGH_NODES))
    if fill_type == TABLE_FIXED_LENGTH:
        for idx in range(0,user_columns.__len__()):
            if user_columns[idx].get(COLUMN_MAX_LENGTH) is None:
                return Promise.reject(CreateTableResponse(False, CreateTableError.FIELD_MAX_LENGTH_REQUIRED))
        if key_max_size <= 0:
            return Promise.reject(CreateTableResponse(False, CreateTableError.KEY_MAX_LENGTH_REQUIRED))
    # Create request
    server_list = create_server_list_from_dict(servers)
    # Notice add 1 to escape factor to allocate the correct size
    column_list = create_column_list(user_columns, fill_type, escape_factor+1, key_max_size=key_max_size)
    table_description = {
        "table_conventional_name": name,
        "table_category": "main",
        "table_clone_name": "",
        "table_main_name": "",
        "table_tsynch_name": "",
        "table_level_for_read": 0,
        "table_level_for_write": 0,
        "table_level_for_modify": 0,
        "use_default_for_table_max_size": "yes" if table_max_size == 1 else "no",
        "use_default_for_tablet_max_size": "yes" if tablet_max_size == 1 else "no",
        "table_max_size_byte": table_max_size,  # Ignored when use_default_for_table_max_size is yes
        "tablet_max_size_byte": tablet_max_size,   # Ignored when use_default_for_tablet_max_size is yes
        "table_fill_type": fill_type,
        "record_padded_length_mod": 1000,
        "replication_factor": replication,
        "n_columns": column_list.__len__(),
        "primary_index_column": COLUMN_NAME_KEY,
        "output_records_type": "straight_row",
        "output_json_generation_mode": "standard",
        "table_strong_synchronization": "off",
        "table_allocation_servers": server_list,
        "column_descriptions": column_list,
    }

    query = {
        "action": ACTION_TABLE_CREATE
    }

    body = {
        "endpoint": TABLES_ENDPOINT,
        "table_type": USER_TABLE,
        "table_description": table_description
    }

    create_request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query, body=json.dumps(body).encode('ascii'))
    return RestManager().submit(create_request, CreateTableResponse.from_http_response)