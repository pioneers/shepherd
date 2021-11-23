import threading
import json
import socket
import selectors
import time


# when using YDL, please do:
# from ydl import ydl_send, ydl_start_read
# since only those two methods are meant for public consumption

SERVER_ADDR = ('127.0.0.1', 5001) # doesn't need to be available on network
CLIENT_THREAD = None

def ydl_start_read(receive_channel, queue, put_json=False):
    '''
    Takes in receiving channel name (string), queue (Python queue object).
    Takes whether to add received items to queue as JSON or Python dict.
    Creates thread that receives any message to receiving channel and adds
    it to queue as tuple (header, dict). Multiple calls to ydl_start_read
    with the same target will replace the old queue.
    header: string
    dict: Python dictionary
    '''
    start_client_thread_if_not_alive()
    if receive_channel not in CLIENT_THREAD.open_targets:
        send_message(CLIENT_THREAD.conn, receive_channel, "")
        # sending an empty string is a special message that means "subscribe to channel"
    CLIENT_THREAD.open_targets[receive_channel] = (queue, put_json)

def ydl_send(target_channel, header, dic=None):
    '''
    Send header and dictionary to target channel (string)
    '''
    start_client_thread_if_not_alive()
    if dic is None:
        dic = {}
    json_str = json.dumps([header, dic])
    send_message(CLIENT_THREAD.conn, target_channel, json_str)



def start_client_thread_if_not_alive():
    '''
    (internal use only)
    '''
    global CLIENT_THREAD
    if CLIENT_THREAD is None:
        CLIENT_THREAD = ClientThread()
        CLIENT_THREAD.start()

class ClientThread(threading.Thread):
    '''
    (internal use only)
    A thread for sending YDL messages to the YDL server
    Has one connection that it keeps open; the thread
    will die when the connection closes
    '''
    def __init__(self):
        super().__init__()
        self.daemon = True #will be shut down abruptly when main thread dies
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.selobj = ReadObject()
        self.open_targets = {}
        while True:
            try:
                self.conn.connect(SERVER_ADDR)
                return
            except ConnectionRefusedError:
                time.sleep(0.1)

    def run(self):
        while True:
            try: # try statement needed because windows sucks and throws an 10054 
                 # connection reset error rather than just returning a 0 byte.
                data = self.conn.recv(1024)  # Should be ready
            except ConnectionResetError:
                data = []
            if len(data) == 0:
                break
            else:
                self.selobj.inb += data
                for target, message in self.selobj:
                    self.forward_message(target, message)
        self.conn.close()

    def forward_message(self, target, message):
        queue, put_json = self.open_targets[target]
        if put_json:
            queue.put(message)
        else:
            queue.put(tuple(json.loads(message)))

def send_message(conn, target, msg):
    '''
    (internal use only)
    Sends a message meant for the given target across conn
    The message format is (len1, len2, str1, str2)
    Note: all 4 components have to be in one conn.sendall call,
    otherwise bad things happen when multiple threads send messages
    at the same time
    '''
    conn.sendall(len(target).to_bytes(4, "little")
               + len(msg).to_bytes(4, "little")
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
        if len(self.inb) < 8:
            raise StopIteration
        len1 = int.from_bytes(self.inb[0:4], "little")
        len2 = int.from_bytes(self.inb[4:8], "little")
        if len(self.inb) < 8 + len1 + len2:
            raise StopIteration
        target_channel = self.inb[8: len1 + 8].decode("utf-8")
        message = self.inb[len1 + 8: len1 + len2 + 8].decode("utf-8")
        self.inb = self.inb[len1 + len2 + 8:]
        return (target_channel, message)

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

def read(sel, subscriptions, conn, obj):
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
                for c in subscriptions[target_channel]:
                    send_message(c, target_channel, message)

def start_backend():
    '''
    (server method - internal use only)
    Starts the YDL server that processes will use
    to communicate with each other
    '''
    subscriptions = {} # a mapping of target names -> list of socket objects
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(SERVER_ADDR)
    sock.listen()
    sock.setblocking(False)
    sel = selectors.DefaultSelector()
    sel.register(sock, selectors.EVENT_READ, None)
    while True:
        events = sel.select(timeout=1) #Windows is bad and needs a timeout here.
        for key, _mask in events:
            if key.data is None:
                accept(sel, key.fileobj)
            else:
                read(sel, subscriptions, key.fileobj, key.data)

if __name__ == "__main__":
    print("Starting YDL server at address:", SERVER_ADDR)
    start_backend()
