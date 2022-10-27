import threading
import json
import socket
import selectors
import time
from typing import Tuple



# Default address for the YDL server. Also used as default arg for client.
# A network of clients should communicate through one server on a designated address.
# if all clients are on one computer, 127.0.0.1 works; if distributed across a local
# network, use 0.0.0.0 instead.
DEFAULT_YDL_ADDR = ('127.0.0.1', 5001) # doesn't need to be available on network


class YDLClient():
    '''
    A client to the YDL network. Listens to a set of channels, and may send messages to
    any channel. Will automatically try to connect to YDL network.
    '''
    def __init__(self, *receive_channels: str, socket_address: Tuple[str, int] = DEFAULT_YDL_ADDR):
        '''
        Waits for connection to open, then subscribes to given receive_channels
        '''
        self._receive_channels = receive_channels
        self._socket_address = socket_address
        self._lock = threading.Lock() # protects all local variables
        self._conn = None    # set in _new_connection()
        self._selobj = None  # set in _new_connection()
        with self._lock:
            self._new_connection()

    def send(self, message: Tuple):
        '''
        The input message is a tuple of (target_channel, stuff...)
        target_channel: str, which channel you want to send to
        stuff: any other stuff you want to send. Must be json serializable.
        May block if disconnected and waiting for a new connection.
        '''
        target_channel = message[0]
        json_str = json.dumps(message[1:])
        while True:
            try:
                send_message(self._conn, target_channel, json_str)
                break
            except (ConnectionResetError, BrokenPipeError):
                pass
            with self._lock:
                self._new_connection()

    def receive(self) -> Tuple:
        '''
        Blocks while waiting for next message. Will try to reconnect if connection is lost.
        '''
        with self._lock:
            while True:
                while True:
                    selobj_iter = iter(self._selobj)
                    try:
                        target, message = next(selobj_iter)
                    except StopIteration:
                        pass
                    else:
                        return (target,) + tuple(json.loads(message))

                    try: # try statement needed because windows sucks and throws an 10054
                        # connection reset error rather than just returning a 0 byte.
                        data = self._conn.recv(1024)  # block
                    except ConnectionResetError:
                        data = []
                    if len(data) == 0:
                        break
                    self._selobj.inb += data
                self._new_connection()

    def _new_connection(self):
        if self._conn is not None:
            self._conn.close()
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._selobj = ReadObject() # in case was in middle of receiving, want this reset
        while True:
            try:
                self._conn.connect(self._socket_address)
                break
            except ConnectionRefusedError:
                time.sleep(0.1)
        for recv_channel in self._receive_channels:
            send_message(self._conn, recv_channel, "")
            # sending an empty string is a special message that means "subscribe to channel"


def send_message(conn, target, msg):
    '''
    (internal use only)
    Sends a message meant for the given target across conn
    The message format is (lenlen, len1, len2, str1, str2)
    Note: all 5 components have to be in one conn.sendall call,
    otherwise bad things happen when multiple threads send messages
    at the same time
    '''
    len1 = len(target)
    len2 = len(msg)
    lenlen = (max(len1, len2).bit_length() + 7) // 8
    conn.sendall(lenlen.to_bytes(1, "little")
               + len1.to_bytes(lenlen, "little")
               + len2.to_bytes(lenlen, "little")
               + target.encode("utf-8")
               + msg.encode("utf-8"))

class ReadObject:
    '''
    (internal use only)
    An iterable object for receiving messages
    Append incoming message bytes to self.inb,
    and then you can loop through the object to get the messages
    '''
    def __init__(self):
        self.inb = b''

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.inb) < 1:
            raise StopIteration
        lenlen = int.from_bytes(self.inb[0:1], "little")
        start = 1 + 2*lenlen # start of target string
        if len(self.inb) < start:
            raise StopIteration
        len1 = int.from_bytes(self.inb[1:1+lenlen], "little")
        len2 = int.from_bytes(self.inb[1+lenlen:start], "little")
        if len(self.inb) < start + len1 + len2:
            raise StopIteration
        target_channel = self.inb[start: start + len1].decode("utf-8")
        message = self.inb[start + len1: start + len1 + len2].decode("utf-8")
        self.inb = self.inb[start + len1 + len2:]
        return (target_channel, message)

def accept(sel, sock, verbose):
    '''
    (server method - internal use only)
    When sock has a connection ready to accept,
    accept the connection and register it in sel
    Note that we want the new connections to be blocking,
    since dealing with non-blocking writes is a pain
    '''
    conn, addr = sock.accept()  # Should be ready
    if verbose:
        print('accepted connection from', addr)
    sel.register(conn, selectors.EVENT_READ, ReadObject())

def read(sel, subscriptions, conn, obj, verbose):
    '''
    (server method - internal use only)
    When conn has bytes ready to read, read those bytes and
    forward messages to the correct subscribers
    '''
    try: # try statement needed because windows sucks and throws an 10054
         # connection reset error rather than just returning a 0 byte.
        data = conn.recv(1024)  # Should be ready
    except ConnectionResetError:
        data = []
    if len(data) == 0:
        if verbose:
            print('closing connection from socket')
        sel.unregister(conn)
        conn.close()
        for lst in subscriptions.values():
            while conn in lst:
                lst.remove(conn)
    else:
        obj.inb += data
        for target_channel, message in obj:
            subscriptions.setdefault(target_channel, [])
            if len(message) == 0:
                # an empty string is a special message that means "subscribe to channel"
                subscriptions[target_channel].append(conn)
            else:
                # forward message to correct subscribers
                for chan in subscriptions[target_channel]:
                    send_message(chan, target_channel, message)

def run_ydl_server(address=None, port=None, verbose=False):
    '''
    (server method - internal use only)
    Runs the YDL server that processes will use
    to communicate with each other
    '''
    if address is None:
        address = DEFAULT_YDL_ADDR[0]
    if port is None:
        port = DEFAULT_YDL_ADDR[1]
    if verbose:
        print("Starting YDL server at address:", (address, port))
    subscriptions = {} # a mapping of target names -> list of socket objects
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((address, port))
    sock.listen()
    sock.setblocking(False)
    sel = selectors.DefaultSelector()
    sel.register(sock, selectors.EVENT_READ, None)
    while True:
        events = sel.select(timeout=1) #Windows is bad and needs a timeout here.
        for key, _mask in events:
            if key.data is None:
                accept(sel, key.fileobj, verbose)
            else:
                read(sel, subscriptions, key.fileobj, key.data, verbose)
