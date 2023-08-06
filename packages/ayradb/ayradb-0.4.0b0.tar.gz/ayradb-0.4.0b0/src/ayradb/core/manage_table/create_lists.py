from ayradb.core.manage_table.column import COLUMN_NUMBER, COLUMN_LABEL, COLUMN_NAME_KEY, COLUMN_SQL_TYPE, SQLFieldType, \
    COLUMN_HTTP_TYPE, HTTPFieldType, COLUMN_MAX_LENGTH, COLUMN_NAME_NOSQL_VALUE
from ayradb.core.manage_table.types import TABLE_FIXED_LENGTH, TABLE_NOSQL


def create_server_list_from_list(server_names: list) -> list:
    for server_name in server_names:
        server_names.append({
            "server_name": server_name
        })
    return server_names


def create_server_list_from_dict(servers: dict) -> list:
    server_names = []
    for server_name in servers.keys():
        server_names.append({
            "server_name": server_name
        })
    return server_names


def create_column_list(user_columns: [], fill_type, escape_factor, key_max_size=-1) -> list:
    columns = [{
        COLUMN_NUMBER: 0,
        COLUMN_LABEL: COLUMN_NAME_KEY,
        COLUMN_SQL_TYPE: SQLFieldType.TEXT,
        COLUMN_HTTP_TYPE: HTTPFieldType.TEXT_HTML
    }]
    if fill_type == TABLE_FIXED_LENGTH:
        # Case fixed length: specify max key size (consider escape factor)
        true_key_max_size=key_max_size*escape_factor
        columns[0][COLUMN_MAX_LENGTH]=true_key_max_size

    if fill_type == TABLE_NOSQL:
        # Case NO_SQL table: add value column
        columns.append({
            COLUMN_NUMBER: 1,
            COLUMN_LABEL: COLUMN_NAME_NOSQL_VALUE,
            COLUMN_SQL_TYPE: SQLFieldType.TEXT,
            COLUMN_HTTP_TYPE: HTTPFieldType.TEXT_HTML
        })
    else:
        is_fixed_length= fill_type == TABLE_FIXED_LENGTH
        for cIdx in range(0,user_columns.__len__()):
            user_columns[cIdx][COLUMN_NUMBER]=cIdx+1
            if is_fixed_length:
                # Case fixed length: specify max field size (consider escape factor)
                column_true_size = user_columns[cIdx][COLUMN_MAX_LENGTH]*escape_factor
                user_columns[cIdx][COLUMN_MAX_LENGTH] = column_true_size
            if user_columns[cIdx].get(COLUMN_SQL_TYPE) is None:
                # Case sql type not specified: defaulted to text
                user_columns[cIdx][COLUMN_SQL_TYPE] = SQLFieldType.TEXT
            if user_columns[cIdx].get(COLUMN_HTTP_TYPE) is None:
                # Case http type not specified: defaulted to text/html
                user_columns[cIdx][COLUMN_HTTP_TYPE] = HTTPFieldType.TEXT_HTML
        columns.extend(user_columns)
    return columns

