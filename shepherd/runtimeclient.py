import time
import threading
import socket
from protos import run_mode_pb2
from protos import start_pos_pb2
from protos import game_state_pb2
from utils import YDL_TARGETS, PROTOBUF_TYPES, UI_HEADER
from ydl import ydl_send

PORT_RASPI = 8101


class RuntimeClient:
    """
    This is a client that connects to the server running on a Raspberry Pi.
    One client is initialized per robot.

    Lifecycle: when the client is created, it makes a socket and a background thread
    to listen to the socket. If the socket disconnects, it will attempt to
    reconnect. If close_connection is called, the socket will close and the
    thread will end.
    """
    def __init__(self, identifier, robot_url):
        # set sock in case close_connection is called before thread is started
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.identifier = identifier
        self.robot_url = robot_url
        self.connected = False
        self.manually_closed = False # whether Shepherd has manually closed this client
        threading.Thread(target=self.__start_recv).start()

    def __repr__(self) -> str:
        return f"RuntimeClient({self.identifier}, {self.robot_url})"

    def __send_msg(self, mode: int, protobuf_obj):
        msg_str = protobuf_obj.SerializeToString()
        msg = bytes(msg_str)
        msglen = len(msg).to_bytes(2, "little")
        if self.connected:
            try:
                self.sock.sendall(bytes([mode]) + msglen + msg)
            except (ConnectionError, OSError) as ex:
                print(f"Error while sending from {self}: {ex}")
        else:
            print("{self} is not connected. Could not send message {msg_str}")

    def send_mode(self, mode):
        """
        Send the Run Mode to Runtime. Example: auto vs teleop
        """
        p = run_mode_pb2.RunMode()
        p.mode = mode
        self.__send_msg(PROTOBUF_TYPES.RUN_MODE, p)

    def send_start_pos(self, pos):
        """
        Send the start position of the robot to Runtime (left or right)
        """
        p = start_pos_pb2.StartPos()
        p.pos = pos
        self.__send_msg(PROTOBUF_TYPES.START_POS, p)

    def send_game_state(self, state):
        """
        Tells Runtime to use the game state, e.g. poison ivy or dehyrdration
        """
        p = game_state_pb2.GameState()
        p.state = state
        self.__send_msg(PROTOBUF_TYPES.GAME_STATE, p)


    def close_connection(self):
        """
        Closes the connection if not already closed. Note that
        sock.shutdown(socket.SHUT_RDWR) sends a fin/eof to the peer
        regardless of how many processes have handles on this socket;
        the other thread will get an OSError while receiving
        """
        if not self.manually_closed:
            self.manually_closed = True # on other thread, know this was deliberate
            try:
                self.sock.shutdown(socket.SHUT_RDWR) # see above docstring
            except (ConnectionError, OSError) as ex:
                print(f"Error shutting down {self}: {ex}")
            self.sock.close() # deallocates


    def send_connection_status_to_ui(self):
        data = {
            "identifier": self.identifier, # TODO: utils
            "connected": self.connected,
            "robot_url": self.robot_url
        }
        ydl_send(YDL_TARGETS.UI, UI_HEADER.ROBOT_CONNECTION, data)


    def __connect_tcp(self, silent=False) -> bool:
        """
        Attempts to connect to the Rasberry PI
        sets self.connected to the connection status
        """
        self.connected = False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2)
            self.sock.connect((self.robot_url, PORT_RASPI))
            self.connected = True
            message = f"Successfully connected to {self}"
        except (ConnectionError, OSError) as ex:
            self.connected = False
            message = f"Error connecting to {self}: {ex}"
        if not silent:
            print(message)
        if self.connected:
            self.sock.settimeout(None)
            self.sock.sendall(bytes([0]))


    def __start_recv(self):
        """
        Until the connection is manually close (controlled by RuntimeClientManager),
        waits to receive an incoming message. If connection fails,
        then tries to reconnect infinitely until self.manually_closed is True
        sends connection status to UI when appropriate
        """
        self.__connect_tcp()
        self.send_connection_status_to_ui()
        if not self.connected:
            return
        while True:
            try:
                received = self.sock.recv(1024)
            except (ConnectionError, OSError) as ex:
                print(f"Error while reading from socket of {self}: {ex}")
                received = False
            print(f"Received message from {self}: ", received)
            if not received:
                self.connected = False
                self.send_connection_status_to_ui()
                if self.manually_closed:
                    self.sock.close() # deallocate from this thread as well
                    return

                print(f"Connection lost to {self}. Trying again...")
                while not self.manually_closed:
                    self.__connect_tcp(silent=True)
                    if self.connected:
                        print(f"Successfully reconnected to {self}")
                        self.send_connection_status_to_ui()
                        break
                    time.sleep(1)
            else:
                # This is where one would process received data, ideally using some function mapping
                # similar to the way it is done in Shepherd.
                pass



class DummyClient:
    """
    A DummyClient just saves a robot_url for the next time
    that Shepherd wants to connect to that url
    """
    def __init__(self, robot_url):
        self.robot_url = robot_url
        self.connected = False

    def send_mode(self, mode):
        pass

    def send_start_pos(self, pos):
        pass

    def send_game_state(self, state):
        pass

    def close_connection(self):
        pass

    def send_connection_status_to_ui(self):
        pass


class RuntimeClientManager:
    def __init__(self):
        self.clients = [DummyClient("")] * 4 # each is a RuntimeClient or a DummyClient

    def connect_client(self, ind, robot_url=None):
        """
        Makes a RuntimeClient at ind and connects it to the
        given robot_url, or to the previous robot_url
        """
        if robot_url is None:
            robot_url = self.clients[ind].robot_url
        if isinstance(self.clients[ind], RuntimeClient):
            self.clients[ind].close_connection()
        self.clients[ind] = RuntimeClient(ind, robot_url)

    def connect_all(self):
        """
        Connects all 4 clients to their saved robot_urls
        """
        for c in range(4):
            self.connect_client(c)

    def foreach(self, fun, *args, **kwargs):
        for client in self.clients:
            if isinstance(client, RuntimeClient):
                fun(client, *args, **kwargs)

    def send_connection_status_to_ui(self):
        self.foreach(RuntimeClient.send_connection_status_to_ui)

    def send_mode(self, mode):
        self.foreach(RuntimeClient.send_mode, mode)

    def send_start_pos(self, pos):
        self.foreach(RuntimeClient.send_start_pos, pos)

    def send_game_state(self, state):
        self.foreach(RuntimeClient.send_game_state, state)

    def reset(self):
        """
        Closes all connections, and
        sets all clients to DummyClients to save the robot_urls
        """
        self.foreach(RuntimeClient.close_connection)
        self.clients = [DummyClient(c.robot_url) for c in self.clients]
