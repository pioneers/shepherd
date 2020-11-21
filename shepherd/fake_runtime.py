import socket
import sys
from protos import run_mode_pb2
from protos import text_pb2
from Utils import *

class TestSocket:

    def __init__(self):
        self.connection = self.connect_tcp()
        self.connection.recv(1)

    def receive(self):
        while True:
            print("incoming")
            msg_type = int.from_bytes(self.connection.recv(1), "big")
            print("msg_type: " + str(msg_type))
            msg_length = int.from_bytes(self.connection.recv(2), "big")
            print("msg_length: " + str(msg_length))
            msg = self.connection.recv(msg_length)
            # decode message todo: these are probably wrong, don't line up in runtime

            if msg_type == PROTOBUF_TYPES.TEXT: #shouldn't msg_type be 4? not sure, am asking runtime in slack
                pb = text_pb2.Text()
                pb.ParseFromString(msg)
            elif msg_type == PROTOBUF_TYPES.RUN_MODE:
                pb = run_mode_pb2.RunMode()
                pb.ParseFromString(msg)
                print("received data: " + str(pb.mode))
            else:
                # error
                print("error")

            

    def set_mode(self, mode):
        # create protobuf
        run_mode = run_mode_pb2.RunMode()
        run_mode.mode = mode
        bytearr = bytearray(run_mode.SerializeToString())
        self.connection.send(bytearr)


    def set_start_pos(self, pos):
        start_pos = start_pos_pb2.StartPos()
        start_pos.pos = pos
        bytearr = bytearray(start_pos.SerializeToString())
        self.connection.send(bytearr)

    # todo: some way to detect connection/if a connection was dropped (heartbeat? some other way?)

    def connect_tcp(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 8101))
        server.listen(1)
        (connection, client_address) = server.accept()
        return connection


socket = TestSocket()
socket.connection.send(b'\x02')
text = text_pb2.Text()
text.payload.append("wieofw")
bytearr = bytearray(text.SerializeToString())
print(len(bytearr))
socket.connection.send(b'\x00\x08') # hardcoded in, really should be len(bytearr), truncated to 2 bits
socket.connection.send(bytearr)
