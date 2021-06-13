import socket
import selectors
from protos import run_mode_pb2
from protos import start_pos_pb2
from protos import game_state_pb2
from utils import PROTOBUF_TYPES

SERVER_ADDR = ("127.0.0.1", 8101)



def send_message(conn, mode: int, protobuf_obj):
    msg_str = protobuf_obj.SerializeToString()
    msg = bytes(msg_str)
    msglen = len(msg).to_bytes(2, "little")
    try:
        conn.sendall(bytes([mode]) + msglen + msg)
    except (ConnectionError, OSError) as ex:
        print(f"Error while sending message: {ex}")



class ReadObject:
    '''
    An iterable object for receiving messages
    Append incoming message bytes to self.inb, 
    and then you can loop through the object to get the messages
    '''
    def __init__(self):
        self.got_indentification = False
        self.inb = b''

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.inb) < 9 and not self.got_indentification:
            self.got_indentification = True
            print(f"identification byte: {self.inb[0]}")
            self.inb = self.inb[1:]
        if len(self.inb) < 3:
            raise StopIteration
        msg_type = int.from_bytes(self.inb[0:1], "little")
        msg_len = int.from_bytes(self.inb[1:3], "little")
        if len(self.inb) < 3 + msg_len:
            raise StopIteration
        msg_bytes = self.inb[3: msg_len + 3]
        self.inb = self.inb[msg_len + 3:]

        if msg_type == PROTOBUF_TYPES.RUN_MODE:
            pb = run_mode_pb2.RunMode()
            pb.ParseFromString(msg_bytes)
            return "received run mode: " + str(pb.mode)
        if msg_type == PROTOBUF_TYPES.START_POS:
            pb = start_pos_pb2.StartPos()
            pb.ParseFromString(msg_bytes)
            return "received start pos: " + str(pb.pos)
        if msg_type == PROTOBUF_TYPES.GAME_STATE:
            pb = game_state_pb2.GameState()
            pb.ParseFromString(msg_bytes)
            return "received game state: " + str(pb.state)
        return "invalid protobuf type"

def accept(sel, sock):
    '''
    (server method - internal use only)
    When sock has a connection ready to accept,
    accept the connection and register it in sel
    Note that we want the new connections to be blocking,
    since dealing with non-blocking writes is a pain
    '''
    conn, addr = sock.accept()  # Should be ready
    print('accepted connection from', addr)
    sel.register(conn, selectors.EVENT_READ, ReadObject())

def read(sel, conn, obj):
    '''
    (server method - internal use only)
    When conn has bytes ready to read, read those bytes and
    forward messages to the correct subscribers
    '''
    data = conn.recv(1024)  # Should be ready
    if len(data) == 0:
        print('closing connection from socket')
        sel.unregister(conn)
        conn.close()
    else:
        obj.inb += data
        for message in obj:
            print(message)

def start_backend():
    '''
    (server method - internal use only)
    Starts the YDL server that processes will use
    to communicate with each other
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(SERVER_ADDR)
    sock.listen()
    sock.setblocking(False)
    sel = selectors.DefaultSelector()
    sel.register(sock, selectors.EVENT_READ, None)
    while True:
        events = sel.select(timeout=None)
        for key, _mask in events:
            if key.data is None:
                accept(sel, key.fileobj)
            else:
                read(sel, key.fileobj, key.data)

if __name__ == "__main__":
    print("Starting fake runtime server at address:", SERVER_ADDR)
    start_backend()

