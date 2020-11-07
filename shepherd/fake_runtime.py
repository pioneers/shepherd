import socket
import sys
from protos import run_mode_pb2

class TestSocket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self):
        self.sock.connect(("127.0.0.1", 8101))

socket = TestSocket()
socket.connect()
socket.sock.send(b'\x00')
run_mode = run_mode_pb2.RunMode()
run_mode.mode = run_mode_pb2.ESTOP
bytearr = bytearray(run_mode.SerializeToString())
print(bytearr)
socket.sock.send(b'\x00\x02') # hardcoded in, really should be len(bytearr), truncated to 2 bits
socket.sock.send(bytearr)
