import time
import threading
import socket
from protos import run_mode_pb2
from protos import start_pos_pb2
from protos import gamestate_pb2
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
    def __init__(self, ind, robot_ip):
        self.ind = ind
        self.robot_ip = robot_ip
        self.sock = None
        self.connected = False
        self.manually_closed = False # whether Shepherd has manually closed this client
        # note that the first connect_tcp has to be in main thread,
        # because otherwise close_connection could be called before first connection
        self.__connect_tcp(silent=(robot_ip==""))
        self.send_connection_status_to_ui()
        if self.connected:
            threading.Thread(target=self.__start_recv, daemon=True).start()

    def __repr__(self) -> str:
        return f"RuntimeClient({self.ind}, {self.robot_ip})"

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
            print(f"{self} is not connected. Could not send message {msg_str}")

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
        p = gamestate_pb2.GameState()
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
                if self.connected:
                    print(f"Error shutting down {self}: {ex}")
            self.sock.close() # deallocates


    def send_connection_status_to_ui(self):
        data = {
            "ind": self.ind,
            "connected": self.connected,
            "robot_ip": self.robot_ip
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
            self.sock.connect((self.robot_ip, PORT_RASPI))
            self.connected = True
            message = f"Successfully connected to {self}"
        except (ConnectionError, OSError) as ex:
            self.connected = False
            message = f"Error connecting to {self}: {ex}"
        if not silent:
            print(message)
        if self.connected:
            self.sock.settimeout(None)
            # send 0 byte so that Runtime knows it's Shepherd
            self.sock.sendall(bytes([0]))


    def __start_recv(self):
        """
        Until the connection is manually close (controlled by RuntimeClientManager),
        waits to receive an incoming message. If connection fails,
        then tries to reconnect infinitely until self.manually_closed is True
        sends connection status to UI when appropriate
        """
        while True:
            try:
                received = self.sock.recv(1024)
                print(f"Received message from {self}: ", received)
            except (ConnectionError, OSError) as ex:
                print(f"Error while reading from socket of {self}: {ex}")
                received = False
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



class RuntimeClientManager:
    def __init__(self):
        self.clients = [RuntimeClient(i, "") for i in range(4)]

    def connect_client(self, ind: int, robot_ip: str):
        """
        Makes a RuntimeClient at ind and connects it to the
        given robot_ip, terminating any previous connection
        """
        self.clients[ind].close_connection()
        self.clients[ind] = RuntimeClient(ind, robot_ip)

    def reconnect_all(self):
        """
        Reconnects all clients to their saved robot_ips
        (terminates existing connections - no need for close_all before)
        """
        for c in range(len(self.clients)):
            self.connect_client(c, self.clients[c].robot_ip)

    def foreach(self, fun, *args, **kwargs):
        for client in self.clients:
            fun(client, *args, **kwargs)

    def send_connection_status_to_ui(self):
        self.foreach(RuntimeClient.send_connection_status_to_ui)

    def send_mode(self, mode):
        self.foreach(RuntimeClient.send_mode, mode)

    def send_start_pos(self, pos):
        self.foreach(RuntimeClient.send_start_pos, pos)

    def send_game_state(self, state):
        self.foreach(RuntimeClient.send_game_state, state)

    def close_all(self):
        self.foreach(RuntimeClient.close_connection)
