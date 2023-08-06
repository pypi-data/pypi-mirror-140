__all__ = ['RestManager']

import time
from dataclasses import dataclass
from threading import Thread, Lock, Condition

from ayradb.rest.http.response import Response, Header
from ayradb.rest.http.request import Request
from ayradb.rest.promise import Promise
from ayradb.rest.socket.wrapper import CherrySocketWrapper
from ayradb.utils.singleton import Singleton
from ayradb.core.keep_alive.request import generate_keep_alive_promise

DISCONNECTION_TIME = 5  # 10 seconds -> keep 2 second margin
MAX_CONN = 1
MAX_CONN_ON_NODE = 1
SLEEP_ADDING_CONNECTION = 0.00005  # 50us
SLEEP_EMPTY_QUEUE_SEC = 0.00005  # 50us
SLEEP_SHUTDOWN_CONTROLLER = 0.0001  # 100us
SLEEP_TCP_BUFFER_EMPTY = 0.00001  # 10us
MIN_NON_INFO_STATUS_CODE = 200


@dataclass
class RestManager(metaclass=Singleton):
    lock: Lock
    condition: Condition
    process: bool
    disconnect: bool
    conn_on_node: dict
    connections: int
    connections_dict: dict
    promises_list: list
    long_tasks_ips: list
    long_tasks_lock: Lock

    def __init__(self):
        self.process = False
        self.disconnect = False
        self.lock = Lock()
        self.updating_runtime_data = False
        self.connections = 0
        self.conn_on_node = {}
        self.connections_dict = {}
        self.promises_lists_dict = {}
        self.lock_dict = {}
        self.condition = Condition(lock=self.lock)
        self.conn_on_node = {}
        self.long_tasks_ips = []
        self.long_tasks_lock = Lock()

    def connect(self, ip, port=None):
        self.lock.acquire()
        connections = self.conn_on_node.get(ip)
        if self.connections < MAX_CONN and \
                (connections is None or connections < MAX_CONN_ON_NODE):
            # A new connection can be established
            socket = None
            if port is None:
                socket = CherrySocketWrapper(ip)
            else:
                socket = CherrySocketWrapper(ip, port=port)
            socket_id = self.connections
            self.long_tasks_lock.acquire()
            self.long_tasks_ips.append((ip, socket.port))
            self.long_tasks_lock.release()
            self.connections_dict[socket_id] = socket
            self.promises_lists_dict[socket_id] = []
            self.lock_dict[socket_id] = Lock()
            self.connections += 1
            # Update connection on node counter
            if connections is None:
                # Add node to connection list
                self.conn_on_node[ip] = 1
            else:
                # Increment node connections
                self.conn_on_node[ip] = self.conn_on_node[ip] + 1
            self.lock.release()
            curr_th = Thread(target=self._process_data_exchange, args=(socket_id,))
            curr_th.start()
            with self.condition:
                while not self.process:
                    # Wait for thread connection setup
                    self.condition.wait()
        else:
            self.lock.release()

    def is_connected(self):
        self.lock.acquire()
        is_processing = self.process
        self.lock.release()
        return is_processing

    def stop_processing(self):
        self.lock.acquire()
        self.disconnect = True
        self.lock.release()
        th = Thread(target=self.__manage_stop)
        th.start()

    def __manage_stop(self):
        self.lock.acquire()
        while self.connections > 0:
            self.lock.release()
            time.sleep(SLEEP_SHUTDOWN_CONTROLLER)
            self.lock.acquire()
        self.process = False
        self.lock.release()

    def _process_data_exchange(self, socket_id):
        socket: CherrySocketWrapper = self.connections_dict[socket_id]
        promises_list: list = self.promises_lists_dict[socket_id]
        lock: Lock = self.lock_dict[socket_id]
        # Last msg received time (initialize here since connection is open)
        last_rcv_time = time.time()
        # Create buffer for response bytes
        res_buffer = b''
        with self.condition:
            self.process = True
            # Notify main thread that socket thread is
            # ready to process requests
            self.condition.notify()
        while not self.disconnect:
            response_parsed = False
            res = Response()
            last_read_len = 0
            promise = None
            is_promise_keep_alive = False
            while not response_parsed:
                # Parse responses related to request sent
                res_buffer += socket.read_available_bytes()
                curr_read_len = res_buffer.__len__()
                if curr_read_len == last_read_len:
                    # No new bytes
                    if res_buffer.__len__() == 0:
                        # Case nothing received from ayra
                        if time.time() - last_rcv_time > DISCONNECTION_TIME and not is_promise_keep_alive:
                            lock.acquire()
                            is_promise_keep_alive = True
                            promise = generate_keep_alive_promise()
                            req = promise.get_request()
                            req.upsert_header(Header.HOST, socket.ip)
                            socket.write(req.to_byte_array())
                            lock.release()
                        if self.disconnect:
                            break
                    # Sleep
                    time.sleep(SLEEP_TCP_BUFFER_EMPTY)
                else:
                    last_read_len = curr_read_len
                    last_rcv_time = time.time()
                bytes_read = res.from_byte_array(res_buffer)
                if bytes_read > 0:
                    # Response found in buffer
                    if last_read_len > bytes_read:
                        res_buffer = res_buffer[bytes_read:last_read_len]
                    else:
                        res_buffer = b''
                    # Update buffer length of current read
                    last_read_len = res_buffer.__len__()
                    try:
                        if promise is None:
                            lock.acquire()
                            promise = promises_list.pop(0)
                            lock.release()
                        if res.status_code >= MIN_NON_INFO_STATUS_CODE:
                            # Case non informational response [>=200]
                            promise.submit(res)
                            response_parsed = True
                            promise = None
                            is_promise_keep_alive = False
                        else:
                            # Case informational response [1xx]
                            promise.submit_informational(res)
                            res = Response()
                    except IndexError:
                        # Informational not paired to a request
                        # Ignore and get ready for another response
                        res = Response()
                        lock.release()

        self.lock.acquire()
        self.connections -= 1
        self.conn_on_node[socket.ip] -= 1
        socket.close()
        self.lock.release()
        return True

    def submit_to_long_queue(self, request: Request, build: type(lambda x: Response)):
        promise = Promise(request, build)
        self.long_tasks_lock.acquire()
        while self.long_tasks_ips.__len__() == 0:
            self.long_tasks_lock.release()
            time.sleep(SLEEP_EMPTY_QUEUE_SEC)
            self.long_tasks_lock.acquire()
        ip, port = self.long_tasks_ips.pop(0)
        self.long_tasks_lock.release()
        socket = CherrySocketWrapper(ip, port=port)
        socket.write(request.to_byte_array())
        Thread(target=self.__manage_long_queue_response, args=(socket, promise)).start()
        return promise

    def __manage_long_queue_response(self, socket: CherrySocketWrapper, promise: Promise):
        response_parsed = False
        res_buffer = b''
        res = Response()
        last_read_len = 0
        while not response_parsed:
            # Parse responses related to request sent
            res_buffer += socket.read_available_bytes()
            curr_read_len = res_buffer.__len__()
            if curr_read_len == last_read_len:
                # No new bytes
                if res_buffer.__len__() == 0:
                    if self.disconnect:
                        break
                # Sleep
                time.sleep(SLEEP_TCP_BUFFER_EMPTY)
            else:
                last_read_len = curr_read_len
            bytes_read = res.from_byte_array(res_buffer)
            if bytes_read > 0:
                # Response found in buffer
                if last_read_len > bytes_read:
                    res_buffer = res_buffer[bytes_read:last_read_len]
                else:
                    res_buffer = b''
                # Update buffer length of current read
                last_read_len = res_buffer.__len__()
                if res.status_code >= MIN_NON_INFO_STATUS_CODE:
                    # Case non informational response [>=200]
                    if res.last_chunk or not res.chunked:
                        promise._close()
                        response_parsed = True
                    promise.submit(res)
                else:
                    # Case informational response [1xx]
                    promise.submit_informational(res)
                # Create a new response object for the next chunk
                res = Response()
        self.long_tasks_lock.acquire()
        self.long_tasks_ips.append((socket.ip, socket.port))
        self.long_tasks_lock.release()
        socket.close()

    def submit(self, request: Request, build: type(lambda x: Response)):
        # Create promise and set promise id in header
        promise = Promise(request, build)
        # TODO use dict len to block insertion
        promise_id = promise.cID
        # Select a connection according to promise id
        connection_id = promise_id % self.connections
        socket: CherrySocketWrapper = self.connections_dict[connection_id]
        promise_list: list = self.promises_lists_dict[connection_id]
        lock: Lock = self.lock_dict[connection_id]
        # Add missing headers
        request.upsert_header(Header.CONNECTION, "Keep-Alive")
        request.upsert_header(Header.HOST, socket.ip)
        lock.acquire()
        while promise_list.__len__() >= 32:
            lock.release()
            time.sleep(SLEEP_EMPTY_QUEUE_SEC)
            lock.acquire()
        promise_list.append(promise)
        socket.write(request.to_byte_array())
        lock.release()
        return promise
