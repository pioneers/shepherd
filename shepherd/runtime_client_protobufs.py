import json
import threading
import time
import queue
import gevent # pylint: disable=import-error
from protos import text_pb2
from protos import run_mode_pb2
from protos import start_pos_pb2
from Utils import *
from LCM import *
import socket

PORT_RASPI = 8101

class RuntimeClient:

    def __init__(self, host_url):
        self.host_url = host_url
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_tcp()
        # send 0 byte so that Runtime knows it's Shepherd
        self.sock.send(bytes([0]))
        

    def receive_challenge_data(self):
        print("incoming")
        msg_type = int.from_bytes(self.sock.recv(1), "big")
        print("msg_type: " + str(msg_type))
        msg_length = int.from_bytes(self.sock.recv(2), "big")
        print("msg_length: " + str(msg_length))
        msg = self.sock.recv(msg_length)

        if msg_type == PROTOBUF_TYPES.CHALLENGE_DATA:
            pb = text_pb2.Text()
            pb.ParseFromString(msg)
            print("received data: " + pb.payload[0])
        else:
            # error
            print("invalid protobuf type")


    def send_mode(self, mode): 
        proto_type = bytearray([0])
        self.sock.send(proto_type)
        run_mode = run_mode_pb2.RunMode()
        run_mode.mode = mode
        bytearr = bytearray(run_mode.SerializeToString())
        self.sock.send(bytearray([len(bytearr)]))
        self.sock.send(bytearr)


    def send_start_pos(self, pos):
        proto_type = bytearray([1])
        self.sock.send(proto_type)
        start_pos = start_pos_pb2.StartPos()
        start_pos.pos = pos
        bytearr = bytearray(start_pos.SerializeToString())
        self.sock.send(len(bytearr).to_bytes(2, "big"))
        self.sock.send(bytearr)


    def send_challenge_data(self, data):
        proto_type = bytearray([2])
        self.sock.send(proto_type)
        text = text_pb2.Text()
        text.payload.extend(data)
        bytearr = bytearray(text.SerializeToString())
        self.sock.send(len(bytearr).to_bytes(2, "big"))
        self.sock.send(bytearr)


    def connect_tcp(self):
        self.sock.connect((self.host_url, PORT_RASPI))

class RuntimeClientManager:

    def __init__(self):
        self.clients = []

    def get_client(self, host_url):
        print("client " + str(host_url) + " started")
        client = RuntimeClient(host_url)
        self.clients.append(client)

    def get_clients(self, host_urls):
        for host_url in host_urls:
            thr = threading.Thread(target=self.get_client, args=[host_url])
            thr.start()

    def receive_challenge_data(self, client):
        client.receive_challenge_data()

    def receive_all_challenge_data(self):
        for client in self.clients:
            thr = threading.Thread(target=self.receive_challenge_data, args=[client])
            thr.start()

    def send_mode(self, mode):
        for client in self.clients:
            client.send_mode(mode)

    def send_start_pos(self, pos):
        for client in self.clients:
            client.send_start_pos(pos)

    def send_challenge_data(self, data):
        for client in self.clients:
            client.send_challenge_data(data)

read = False
manager = RuntimeClientManager()
manager.get_clients(["8101", "5000"])
while True:
    if len(manager.clients) == 2 and not read:
        manager.receive_all_challenge_data()
        manager.send_challenge_data(["hello"])
        read = True
