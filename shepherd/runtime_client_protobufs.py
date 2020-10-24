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
        
    # def receive(self):
    #     while True:
    #         buf = connection.recv(4)
    def set_mode(self, mode):
        # create protobuf
        run_mode = run_mode_pb2.RunMode()
        run_mode.mode = mode
        bytearr = bytearray(run_mode.SerializeToString())
        self.connection.send(bytearr)

    # connect to raspberry pi

    # get data to be a byte array

    # socket.send data

    def connect_tcp(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(PORT_RASPI)
        server.connect()
        connection, client_address = server.accept()
        server.close()
        return connection

