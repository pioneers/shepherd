import threading
from protos import text_pb2
from protos import run_mode_pb2
from protos import start_pos_pb2
from protos import game_state_pb2
from Utils import *
from Robot import Robot
import socket

PORT_RASPI = 8101


class RuntimeClient:
    """
    This is a client that connects to the server running on a Raspberry Pi. 
    xOne client is initialized per robot.
    """
   
    def __init__(self, host_url, robot):
        self.host_url = host_url
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_tcp()
        # send 0 byte so that Runtime knows it's Shepherd
        self.sock.send(bytes([0]))
        self.robot: Robot = robot

    def receive_challenge_data(self):
        """
        Receive the results of the coding challenges, immediately after send_challenge_data is called.
        """
        print("incoming challenge data")
        msg_type = int.from_bytes(self.sock.recv(1), "little")
        print("msg_type: " + str(msg_type))
        msg_length = int.from_bytes(self.sock.recv(2), "little")
        print("msg_length: " + str(msg_length))
        msg = self.sock.recv(msg_length)

        if msg_type == PROTOBUF_TYPES.CHALLENGE_DATA:
            pb = text_pb2.Text()
            pb.ParseFromString(msg)
            # TODO: format payload to be a list of booleans
            payload = pb.payload
            self.robot.coding_challenge = payload
        else:
            # error
            print("invalid protobuf type")

    def send_mode(self, mode):
        """
        Send the Run Mode to Runtime. Example: auto vs teleop.
        """
        proto_type = bytearray([PROTOBUF_TYPES.RUN_MODE])
        self.sock.send(proto_type)
        run_mode = run_mode_pb2.RunMode()
        run_mode.mode = mode
        bytearr = bytearray(run_mode.SerializeToString())
        self.sock.send(len(bytearr).to_bytes(2, "little"))
        self.sock.send(bytearr)

    def send_start_pos(self, pos):
        """
        Send the start position of the robot to Runtime (left or right). This will not be used for 2021.
        """
        proto_type = bytearray([PROTOBUF_TYPES.START_POS])
        self.sock.send(proto_type)
        start_pos = start_pos_pb2.StartPos()
        start_pos.pos = pos
        bytearr = bytearray(start_pos.SerializeToString())
        self.sock.send(len(bytearr).to_bytes(2, "little"))
        self.sock.send(bytearr)

    def send_challenge_data(self, data):
        """
        Tells Runtime to execute the coding challenges in {data}, an array of strings with the names of the coding challenges.
        """
        proto_type = bytearray([PROTOBUF_TYPES.CHALLENGE_DATA])
        self.sock.send(proto_type)
        text = text_pb2.Text()
        text.payload.extend(data)
        bytearr = bytearray(text.SerializeToString())
        self.sock.send(len(bytearr).to_bytes(2, "little"))
        self.sock.send(bytearr)
        # Listen for challenge outputs
        self.receive_challenge_data()

    def send_game_state(self, state):
        """
        Tells Runtime to use the game state, e.g. poison ivy or dehyrdration
        """
        proto_type = bytearray([PROTOBUF_TYPES.GAME_STATE])
        self.sock.send(proto_type)
        game_state = game_state_pb2.GameState()
        game_state.state = state
        bytearr = bytearray(game_state.SerializeToString())
        self.sock.send(len(bytearr).to_bytes(2, "little"))
        self.sock.send(bytearr)

    def connect_tcp(self):
        # self.sock.connect(("127.0.0.1", int(self.host_url)))
        self.sock.connect((self.host_url, PORT_RASPI))

    def close_connection(self):
        self.sock.shutdown(socket.SHUT_RDWR) # sends a fin/eof to the peer regardless of how many processes have handles on this socket
        self.sock.close() # deallocates


class RuntimeClientManager:

    def __init__(self):
        self.clients = []

    def __get_client(self, host_url, robot):
        """
        Connects to robot at host_url. This method should not be called because the thread is created in get_clients.
        """
        print("client " + str(host_url) + " started")
        client = RuntimeClient(host_url, robot)
        self.clients.append(client)

    def get_clients(self, host_urls, robots):
        for i in range(len(host_urls)):
            thr = threading.Thread(target=self.__get_client, args=[host_urls[i], robots[i]])
            thr.start()

    def receive_challenge_data(self, client):
        client.receive_challenge_data()

    def receive_all_challenge_data(self):
        for client in self.clients:
            thr = threading.Thread(
                target=self.receive_challenge_data, args=[client])
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

    def send_game_state(self, state):
        for client in self.clients:
            client.send_game_state(state)
        
    def reset(self):
        for client in self.clients:
            client.close()
        self.clients = []


"""
Sample code that connects to one robot and sends dummy challenge data.

NUM_ROBOTS = 1
read = False
manager = RuntimeClientManager()
manager.get_clients(["192.168.29.1"])  # should be IP addresses in actual use
while True:
    if len(manager.clients) == NUM_ROBOTS and not read:
        # manager.receive_all_challenge_data()
        # manager.send_challenge_data(["hello"])
        manager.send_challenge_data(["12"])
        # manager.check_connections()
        read = True
"""
