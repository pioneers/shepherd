import socket
import sys
from protos import run_mode_pb2
from protos import text_pb2
from protos import start_pos_pb2
from Utils import *

class TestSocket:

    def __init__(self):
        self.connection = self.connect_tcp()
        self.connection.recv(1)

    def receive(self):
        while True:
            print("waiting")
            msg_type = int.from_bytes(self.connection.recv(1), "big")
            print("msg_type: " + str(msg_type))
            msg_length = int.from_bytes(self.connection.recv(2), "big")
            print("msg_length: " + str(msg_length))
            msg = self.connection.recv(msg_length)

            if msg_type == PROTOBUF_TYPES.RUN_MODE:
                pb = run_mode_pb2.RunMode()
                pb.ParseFromString(msg)
                print("received run mode: " + str(pb.mode))
                pb.ParseFromString(msg)
            elif msg_type == PROTOBUF_TYPES.START_POS:
                pb = start_pos_pb2.StartPos()
                pb.ParseFromString(msg)
                print("received start pos: " + str(pb.pos))
            elif msg_type == PROTOBUF_TYPES.CHALLENGE_DATA:
                pb = text_pb2.Text()
                pb.ParseFromString(msg)
                print("received challenge data: " + str(pb.payload[0]))
            else:
                # error
                print("invalid protobuf type")
            

    def connect_tcp(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 5000))
        server.listen(1)
        (connection, client_address) = server.accept()
        return connection


socket = TestSocket()
socket.connection.send(b'\x02')
text = text_pb2.Text()
text.payload.append("wieofw")
bytearr = bytearray(text.SerializeToString())
socket.connection.send(b'\x00\x08') # hardcoded in, really should be len(bytearr), truncated to 2 bits
socket.connection.send(bytearr)
socket.receive()
