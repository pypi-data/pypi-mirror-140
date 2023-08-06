__all__ = ['Stream']

import time

from dataclasses import dataclass

from threading import Lock

from ayradb.rest.http.response import Response

WAIT_SLEEP = 0.00005  # 50us


class StreamClosedException(Exception):
    pass


@dataclass
class Stream:

    __res: list
    res_method: type(lambda x: Response)
    __lock: Lock
    __is_closed: bool

    def __init__(self, build: type(lambda x: Response)):
        self.__res = []
        self.res_method = build
        self.__lock = Lock()
        self.__is_closed = False

    def size(self):
        self.__lock.acquire()
        size = self.__res.__len__()
        self.__lock.release()
        return size

    def is_empty(self):
        return self.size() <= 0

    def take(self):
        self.__lock.acquire()
        elements = self.__res
        self.__res = []
        self.__lock.release()
        return elements

    def take_when_available(self, min_size=1):
        size = self.size()
        if self.is_closed() and size == 0:
            raise StreamClosedException
        while self.size() < min_size:
            time.sleep(WAIT_SLEEP)
        return self.take()

    def _get_first(self):
        self.__lock.acquire()
        first_el = self.__res[0]
        self.__lock.release()
        return first_el

    def _submit(self, response):
        self.__lock.acquire()
        self.__res.append(self.res_method(response))
        self.__lock.release()

    def _close(self):
        self.__lock.acquire()
        self.__is_closed = True
        self.__lock.release()

    def is_closed(self):
        self.__lock.acquire()
        is_closed = self.__is_closed
        self.__lock.release()
        return is_closed and self.is_empty()
