from ayradb.core.manage_table.column import *
from ayradb.core.manage_table.create_lists import create_server_list_from_list, create_column_list
from ayradb.core.manage_table.types import TABLE_FIXED_LENGTH
from ayradb.rest.promise import Promise
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.http.request import Request
from ayradb.core.endpoints.endpoints import SYSTEM_ENDPOINT, TABLES_ENDPOINT
from ayradb.core.manage_table.restructure.response import RestructureTableResponse, RestructureTableError

import json

ACTION = "table_restructure"
MINIMUM_REPLICATION = 1
DEFAULT_ESCAPE_FACTOR = 1

def restructure_table(name, fill_type, user_columns:[], servers: [], replication, table_max_size, key_max_size, escape_factor=DEFAULT_ESCAPE_FACTOR):

    server_list = create_server_list_from_list(servers)
    query = {
            "action": ACTION
        }

    body = {
        "table_name": name,
        "table_clone_name": "",
        "endpoint": TABLES_ENDPOINT,
        "table_description": "table_description",
        "restructuration_type": "servers",
        "server_list": server_list
    }
    if table_max_size is not None:
        body["new_table_max_size_bytes"] = table_max_size
    if replication is not None:
        if replication > MINIMUM_REPLICATION > servers.__len__():
            return Promise.reject(RestructureTableResponse(False, RestructureTableError.NOT_ENOUGH_NODES))
        body["new_table_replication_factor"] = replication
    if user_columns is not None:
        if fill_type == TABLE_FIXED_LENGTH:
            for idx in range(0, user_columns.__len__()):
                if user_columns[idx].get(COLUMN_MAX_LENGTH) is None:
                    return Promise.reject(RestructureTableResponse(False, RestructureTableError.FIELD_MAX_LENGTH_REQUIRED))
            if key_max_size <= 0:
                return Promise.reject(RestructureTableResponse(False, RestructureTableError.KEY_MAX_LENGTH_REQUIRED))
        column_list = create_column_list(user_columns, fill_type, escape_factor + 1, key_max_size=key_max_size)
        body["new_record_structure"] = column_list

    create_request = Request(Request.METHOD_POST, path=SYSTEM_ENDPOINT, query=query, body=json.dumps(body).encode('ascii'))
    return RestManager().submit(create_request, RestructureTableResponse.from_http_response)
