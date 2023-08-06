# KEY column
COLUMN_NAME_KEY = "key_column"
COLUMN_NAME_NOSQL_VALUE = "value"

# Column build labels
COLUMN_NUMBER = "column_number"
COLUMN_LABEL = "column_label"
COLUMN_SQL_TYPE = "column_sql_type"
COLUMN_HTTP_TYPE = "column_http_type"
COLUMN_MAX_LENGTH="column_max_net_length"

# Column labels provided to users
class Column:
    NAME = COLUMN_LABEL
    MAX_LENGTH = COLUMN_MAX_LENGTH

# Colum types
class SQLFieldType:
    TEXT="TEXT"
    

class HTTPFieldType:
    TEXT_HTML='text\\/html'