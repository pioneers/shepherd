import json
import threading
import time
import queue
import gevent # pylint: disable=import-error
from protos import *
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
            msg_type = self.connection.recv(1)
            msg_length = self.connection.recv(2)
            msg = self.connection.recv(int(msg_length))
            # decode message todo: these are probably wrong, don't line up in runtime

            if msg_type == PROTOBUF_TYPES.TEXT: #shouldn't msg_type be 4? not sure, am asking runtime in slack
                pb = text_pb2.Text()
            else:
                # error

            parsed_data = pb.ParseFromString(msg)
            
            # todo: do stuff with the data
            print("received data:" + parsed_data)


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


    def send_challenge_data(self, data):
        challenge_data = # something
        challenge_data.# something
        bytearr = bytearray(challenge_data.SerializeToString())
        self.connection.send(bytearr)

    # todo: some way to detect connection/if a connection was dropped (heartbeat? some other way?)

    def connect_tcp(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(PORT_RASPI)
        server.connect()
        connection, client_address = server.accept()
        server.close()
        return connection

