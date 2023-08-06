
from dataclasses import dataclass

from ayradb.rest.promise import Promise
from ayradb.core.manage_record.query import query_records


@dataclass
class Query:

    query_string: str

    def __init__(self, query_string):
        self.query_string = query_string

    def execute(self) -> Promise:
        return query_records(self.query_string)
