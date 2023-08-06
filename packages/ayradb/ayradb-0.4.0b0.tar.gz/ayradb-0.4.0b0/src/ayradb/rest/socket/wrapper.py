import socket, select
import time
from dataclasses import dataclass

CHERRY_PORT = 10019
CHUNK_MAX_SIZE = 65536

@dataclass
class CherrySocketWrapper:

    def __init__(self, ip, port = CHERRY_PORT):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.ip = ip
        self.port = port
        self.socket.setblocking(False)

    def read_available_bytes(self):
        buffer_end = False
        buffer = b''
        while not buffer_end:
            try:
                chunk = self.socket.recv(CHUNK_MAX_SIZE)
                buffer += chunk
                if chunk.__len__() < CHUNK_MAX_SIZE:
                    buffer_end = True
            except BlockingIOError:
                buffer_end = True
        return buffer

    def write(self, byte_array):
        self.socket.send(byte_array)
        _, writable, _ = select.select([], [self.socket], [])
        while writable.__len__()<=0:
            _, writable, _ = select.select([], [self.socket], [])

    def close(self):
        self.socket.close()

