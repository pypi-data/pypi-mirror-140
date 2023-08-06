__all__ = ['Table']

from dataclasses import dataclass

from ayradb.core.manage_nodes.get_servers.request import get_servers
from ayradb.core.manage_record.check_existence.request import check_record_existence
from ayradb.core.manage_record.delete.request import delete_record
from ayradb.core.manage_record.read.request import read_record
from ayradb.core.manage_record.scan.request_scan import scan
from ayradb.core.manage_record.scan.request_scan_init import scan_init
from ayradb.core.manage_record.upsert.request import upsert_record
from ayradb.core.manage_table.create.request import MINIMUM_REPLICATION, create_table  #
from ayradb.core.manage_table.create.response import CreateTableResponse, CreateTableError
from ayradb.core.manage_table.delete.request import delete_table
from ayradb.core.manage_table.get_structure.request import get_table_structure
from ayradb.core.manage_table.restructure.request import restructure_table
from ayradb.core.manage_table.truncate.request import truncate_table
from ayradb.core.manage_table.types import TABLE_FIXED_LENGTH, TABLE_PADDED, TABLE_NOSQL
from ayradb.rest.promise import Promise


@dataclass
class Table:

    name: str

    TYPE_FIXED_LENGTH = TABLE_FIXED_LENGTH
    TYPE_PADDED = TABLE_PADDED
    TYPE_NOSQL = TABLE_NOSQL

    def __init__(self, table_name: str):
        self.name = table_name

    def read_record(self, key: str, fields: [] = None) -> Promise:
        return read_record(self.name, key, fields=fields)

    def upsert_record(self, key: str, fields: dict) -> Promise:
        return upsert_record(self.name, key, fields)

    def delete_record(self, key: str, fields: [] = None) -> Promise:
        return delete_record(self.name, key, fields=fields)

    def contains_record(self, key: str) -> Promise:
        return check_record_existence(self.name, key)

    def scan_init(self) -> Promise:
        return scan_init(self.name)

    def scan(self, segment: int, fields: [] = None, last_hash: str = None) -> Promise:
        return scan(self.name, segment, fields=fields, last_hash=last_hash)

    def create(self, fill_type, columns: [] = None, table_max_size=1, key_max_size=-1, replication=MINIMUM_REPLICATION) -> Promise:
        servers_req = get_servers().wait_response()
        if not servers_req.success:
            return Promise.reject(CreateTableResponse(False, CreateTableError.INTERNAL_ERROR))
        
        return create_table(self.name, fill_type, columns, servers_req.servers, key_max_size=key_max_size, table_max_size=table_max_size, replication=replication)

    def restructure(self, columns: [], servers: [], table_max_size=1, replication=MINIMUM_REPLICATION) -> Promise:
        # TODO: check if it works
        return restructure_table(self.name, columns, servers, replication, table_max_size)

    def drop(self) -> Promise:
        return delete_table(self.name)

    def truncate(self) -> Promise:
        return truncate_table(self.name)

    def get_structure(self) -> Promise:
        return get_table_structure(self.name)
