from dataclasses import dataclass
from ayradb.rest.http.header import Header


@dataclass
class Request:

    method: str
    #host: str
    path: str
    query: dict
    headers: dict
    body: bytes

    METHOD_GET = "GET"
    METHOD_POST = "POST"
    METHOD_PUT = "PUT"
    METHOD_DELETE = "DELETE"

    HTTP_PROTO_VERSION = "HTTP/1.1"

    def __init__(self, method, url="", path="", query=None, headers=None, body=b''):
        if headers is None:
            headers = {}
        if query is None:
            query = {}
        self.method = method
        if url != "":
            try:
                url_to_split = url
                try:
                    # Try removing protocol from url
                    url_to_split = url_to_split.split("://")[1]
                except IndexError:
                    # Case relative url (without proto + host)
                    pass
                url_split=url_to_split.split("/")
                self.path = ""
                # Extract path from url:
                i = 1
                while i < url_split.__len__():
                    # TODO: verify partial urls are parsed correctly
                    self.path += "/"+url_split[i]
                    i += 1
                # Extract query from url
                query_split = url_split[url_split.__len__()-1].split("?")
                if query_split.__len__() > 1:
                    self.query = query
            except IndexError:
                raise InvalidUrl("Invalid url format")
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body
        self.headers[Header.CONTENT_LENGTH] = body.__len__()

    def upsert_header(self, key: str, value: str):
        self.headers[key] = value

    def to_byte_array(self):
        query = ""
        index = 0
        for query_param, param_value in self.query.items():
            query += ("?" if index == 0 else "&")+query_param+"="+str(param_value)
            index += 1
        request_string = self.method+" "+self.path+query+" "+Request.HTTP_PROTO_VERSION+"\r\n"
        for header, h_value in self.headers.items():
            request_string += header+": "+str(h_value)+"\r\n"
        request_string += "\r\n"
        request = request_string.encode('utf8')
        request += self.body
        return request


class InvalidUrl(BaseException):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message
