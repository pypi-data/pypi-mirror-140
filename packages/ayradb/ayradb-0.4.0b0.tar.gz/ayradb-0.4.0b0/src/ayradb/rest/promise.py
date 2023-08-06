__all__ = ['Promise']

import time
from dataclasses import dataclass
from threading import Lock

from ayradb.rest.http.request import Request
from ayradb.rest.http.response import Response
from ayradb.rest.stream import Stream

WAIT_SLEEP = 0.00005  # 50us


@dataclass
class Promise:
    __id_count = 0
    __lock = Lock()

    _req: Request
    informational_msgs: []

    def __init__(self, request, build: type(lambda x: Response)):
        self._req = request
        Promise.__lock.acquire()
        self.cID = Promise.__id_count
        Promise.__id_count += 1
        Promise.__lock.release()
        self.__stream = Stream(build)
        self.informational_msgs = []

    def get_request(self):
        return self._req

    def wait_response(self):
        while self.__stream.is_empty():
            time.sleep(WAIT_SLEEP)
        return self.__stream._get_first()

    def submit(self, response):
        self.__stream._submit(response)

    def _close(self):
        self.__stream._close()

    @property
    def stream(self):
        return self.__stream

    def submit_informational(self, response):
        self.informational_msgs.append(response)

    @staticmethod
    def reject(error_object):
        promise = Promise(None, None)
        promise.__stream = error_object
        return promise
