import time
import threading
from protos import text_pb2
from protos import run_mode_pb2
from protos import start_pos_pb2
from protos import game_state_pb2
from Utils import LCM_TARGETS, PROTOBUF_TYPES, UI_HEADER
from LCM import lcm_send, lcm_start_read
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

    def connect_tcp(self, silent=False) -> bool:
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
            self.sock.settimeout(2)
            self.sock.connect((self.host_url, PORT_RASPI))
            message = f"Successfully connected to Robot {self.robot}"
        except Exception as exc:
            connected = False
            message = f"Error connecting to Robot {self.robot}: {exc}"
        if not silent:
            print(message)

        self.is_alive = connected
        self.send_connection_status_to_ui()
        if connected:
            thr = threading.Thread(target=self.start_recv)
            thr.start()
        # send 0 byte so that Runtime knows it's Shepherd
        if self.is_alive:
            self.sock.send(bytes([0]))
        return connected

    def close_connection(self):
        """
        Closes the connection if not already closed.
        """
        if self.is_alive:
            self.is_alive = False
            self.sock.shutdown(socket.SHUT_RDWR) # sends a fin/eof to the peer regardless of how many processes have handles on this socket
            self.sock.close() # deallocates
            self.send_connection_status_to_ui()

    def send_connection_status_to_ui(self):
        data = {
            "team_num": self.robot.number,
            "connected": self.is_alive,
            "custom_ip": self.robot.custom_ip
        }
        lcm_send(LCM_TARGETS.UI, UI_HEADER.ROBOT_CONNECTION, data)

    def start_recv(self):
        """
        While the client exists (controlled by RuntimeClientManager),
        waits to receive an incoming message. If connection fails,
        then tries to reconnect infinitely until either self.client_exists
        is False or the thread is closed in garbage collection.
        """
        while self.client_exists:
            try:
                received = self.sock.recv(1)
            except ConnectionResetError as e:
                print(f"Connection reset error while reading from socket: {e}")
                received = False
            # except socket.timeout as e:
            #     print(f"Ungraceful disconnection from socket: {e}")
            #     received = False
            print(f"Received message from Robot {self.robot}: ", received)
            # received could be False or b'' which means EOF
            if not received:
                # socket has been closed oops
                print(f"Connection lost to Robot {self.robot}. Trying again? {self.client_exists}")
                self.close_connection()
                if self.client_exists:
                    print(f"Attempting to reconnect to robot {self.robot}")
                while self.client_exists:
                    if self.connect_tcp(silent=True):
                        print(f"Successfully reconnected to robot {self.robot}")
                        return
                    time.sleep(1)
                return
            else:
                # This is where one would process received data, ideally using some function mapping
                # similar to the way it is done in Shepherd.
                pass



class RuntimeClientManager:

    def __init__(self):
        self.clients: List[RuntimeClient] = []

    def __get_client(self, host_url, robot):
        """
        Connects to robot at host_url. This method should not be called because the thread is created in get_clients.
        """
        print("client " + str(host_url) + " started")
        client = RuntimeClient(host_url, robot)
        print(f"is client alive in __get_client? {client.is_alive}")
        if client.is_alive:
            self.clients.append(client)

    def send_connection_status_to_ui(self):
        if len(self.clients) > 0:
            for client in self.clients:
                client.send_connection_status_to_ui()
        else:
            lcm_send(LCM_TARGETS.UI, UI_HEADER.ROBOT_CONNECTION, {"connected": False})

    def get_clients(self, host_urls, robots: List[Robot]):
        print(f"called get_clients on {host_urls}")
        for i in range(len(host_urls)):
            robot, host_url = robots[i], host_urls[i]
            robot_nums = [c.robot.number for c in self.clients]
            print(f"Robot nums is {robot_nums}")
            if robot.number in robot_nums:
                index = robot_nums.index(robot.number)
                print(f"Setting client exists of client {self.clients[index]} to False")
                self.clients[index].client_exists = False
                print(f"Closing connection to robot {robot.number}")
                self.clients[index].close_connection()
                self.clients.pop(index)
            else:
                print(f"robot {robot.number} does not exist in robot_nums")
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
