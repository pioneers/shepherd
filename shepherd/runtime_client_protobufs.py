import json
import threading
import time
import queue
import gevent # pylint: disable=import-error
from protos import text_pb2
from protos import run_mode_pb2
from Utils import *
from LCM import *
import socket

HOST_URL = "127.0.0.1"
PORT_RASPI = 8101

class RuntimeClient:

    def __init__(self):
        self.connection = self.connect_tcp()
        # send 0 byte so that Runtime knows it's Shepherd
        self.connection.send(bytes([0]))
        

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
        server.bind((HOST_URL, PORT_RASPI))
        server.listen(1)
        (connection, client_address) = server.accept()
        return connection

class RuntimeClientManager:

    def __init__(self):
        self.clients = []

    def new_client(self):
        client = RuntimeClient()
        self.clients.append(client)

manager = RuntimeClientManager()
manager.new_client()
manager.clients[0].receive()