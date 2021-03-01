import time
import threading
from protos import text_pb2
from protos import run_mode_pb2
from protos import start_pos_pb2
from protos import game_state_pb2
from Utils import *
from LCM import *
from Robot import Robot
import socket
from typing import List

PORT_RASPI = 8101


class RuntimeClient:
    """
    This is a client that connects to the server running on a Raspberry Pi. 
    One client is initialized per robot.
    """
   
    def __init__(self, host_url, robot):
        self.host_url = host_url
        self.robot: Robot = robot
        self.is_alive = False
        self.client_exists = True
        self.connect_tcp()
        # send 0 byte so that Runtime knows it's Shepherd
        if self.is_alive:
            self.sock.send(bytes([0]))

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

    def connect_tcp(self) -> bool:
        """
        - Attempts to connect to the Rasberry PI
        - sets self.is_alive to the connection status
        - sends connection status to UI
        - starts a receiving thread that reads incoming messages and provides heartbeat
        """
        # self.sock.connect(("127.0.0.1", int(self.host_url)))
        connected = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host_url, PORT_RASPI))
        except Exception as exc:
            connected = False
            print(f"Error connecting to Robot {self.robot}: {exc}")
        self.is_alive = connected
        lcm_send(LCM_TARGETS.UI, UI_HEADER.ROBOT_CONNECTION, {"team_num": self.robot.number, "connected": connected})
        if connected:
            thr = threading.Thread(target=self.start_recv)
            thr.start()
        return connected

    def close_connection(self):
        """
        Closes the connection if not already closed.
        """
        self.is_alive = False
        if self.sock.fileno() != -1:
            self.sock.shutdown(socket.SHUT_RDWR) # sends a fin/eof to the peer regardless of how many processes have handles on this socket
            self.sock.close() # deallocates

    def start_recv(self):
        """
        While the client exists (controlled by RuntimeClientManager),
        waits to receive an incoming message. If connection fails,
        then tries to reconnect infinitely until either self.client_exists
        is False or the thread is closed in garbage collection.
        """
        while self.client_exists:
            received = self.sock.recv(1)
            print("RECIEVED IS ", received)
            if not received:
                # socket has been closed oops
                lcm_send(LCM_TARGETS.UI, UI_HEADER.ROBOT_CONNECTION, {"team_num": self.robot.number, "connected": False})
                print(f"Connection lost to Robot {self.robot}, trying again.")
                self.close_connection()
                while self.client_exists:
                    print(f"Attempting to reconnect to robot {self.robot}")
                    if self.connect_tcp():
                        return
                    time.sleep(1)
                return
            else:
                self.is_alive = True



class RuntimeClientManager:

    def __init__(self):
        self.clients: List[RuntimeClient] = []

    def __get_client(self, host_url, robot):
        """
        Connects to robot at host_url. This method should not be called because the thread is created in get_clients.
        """
        print("client " + str(host_url) + " started")
        client = RuntimeClient(host_url, robot)
        if client.is_alive:
            self.clients.append(client)

    def get_clients(self, host_urls, robots: List[Robot]):
        for i in range(len(host_urls)):
            robot, host_url = robots[i], host_urls[i]
            robot_nums = [c.robot.number for c in self.clients]
            if robot.number in robot_nums:
                index = robot_nums.index(robot.number)
                self.clients[index].client_exists = False
                self.clients[index].close_connection()
                self.clients.pop(index)
            thr = threading.Thread(target=self.__get_client, args=[host_url, robot])
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
            try:
                client.send_mode(mode)
            except Exception as exc:
                print(f"Robot {client} failed to be enabled! Big sad :(")

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
            client.client_exists = False
            client.close_connection()
        self.clients: List[RuntimeClient] = []


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
