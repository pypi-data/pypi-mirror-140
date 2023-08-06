__all__ = ['AyraDB']

import time
from dataclasses import dataclass

from ayradb.core.exceptions.invalid_table import InvalidTableName
from ayradb.core.exceptions.connection import InitalizationError
from ayradb.core.manage_nodes.get_servers.request import get_servers
from ayradb.core.manage_nodes.add_node.request import add_node
from ayradb.core.table import Table
from ayradb.core.query import Query
from ayradb.core.validate import validate_table_name
from ayradb.rest.rest_manager import RestManager
from ayradb.rest.promise import Promise

DISCONNECT_SLEEP = 0.1


@dataclass
class AyraDB:

    __ip: str
    validated_names: dict

    def __init__(self, ip="", port=None):
        self.validated_names={}
        if ip != "":
            self.__ip = ip
            RestManager().connect(ip, port=port)
        elif not RestManager().is_connected():
            raise InitalizationError("Please provide a valid ip on first initialization")

    def table(self, table_name) -> Table:
        is_name_valid = self.validated_names.get(table_name)
        if is_name_valid is None:
            # Validate and cache
            is_name_valid = validate_table_name(table_name)
            self.validated_names[table_name] = is_name_valid
        if not is_name_valid:
            raise InvalidTableName("The inserted table name contains invalid characters. Please respect the following regexp: [a-zA-Z0-9_]")
        return Table(table_name)

    def close_connection(self):
        RestManager().stop_processing()
        while RestManager().is_connected():
            time.sleep(DISCONNECT_SLEEP)

    def get_servers(self) -> dict:
        return get_servers()

    def add_node(self, name, ip, hard_disk: []) -> Promise:
        # FIXME: this method is not working
        return add_node(self.name, self.__ip)

    def new_raw_query(self, query_string) -> Query:
        return Query(query_string)

    def remove_node(self, name, ip):
        pass
