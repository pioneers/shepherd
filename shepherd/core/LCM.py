import threading
import json
import socket
import selectors



'''
when using LCM, please do:
from LCM import lcm_send, lcm_start_read
lots of names in here begin with underscores, they are not meant
to be exposed to the outside world
'''

_SERVER_ADDR = ('127.0.0.1', 5001) # doesn't need to be available on network
_CLIENT_THREAD = None

def lcm_start_read(receive_channel, queue, put_json=False):
    '''
    Takes in receiving channel name (string), queue (Python queue object).
    Takes whether to add received items to queue as JSON or Python dict.
    Creates thread that receives any message to receiving channel and adds
    it to queue as tuple (header, dict). Multiple calls to lcm_start_read
    with the same target will replace the old queue.
    header: string
    dict: Python dictionary
    '''
    _start_client_thread_if_not_alive()
    if receive_channel not in _CLIENT_THREAD.open_targets:
        _send_message(_CLIENT_THREAD.conn, receive_channel, "")
    _CLIENT_THREAD.open_targets[receive_channel] = (queue, put_json)

def lcm_send(target_channel, header, dic=None):
    '''
    Send header and dictionary to target channel (string)
    '''
    _start_client_thread_if_not_alive()
    if dic is None:
        dic = {}
    dic['header'] = header
    json_str = json.dumps(dic)
    _send_message(_CLIENT_THREAD.conn, target_channel, json_str)

def _start_client_thread_if_not_alive():
    global _CLIENT_THREAD
    if _CLIENT_THREAD is None:
        _CLIENT_THREAD = _ClientThread()
        _CLIENT_THREAD.start()

class _ClientThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True #will be shut down abruptly when main thread dies
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.selobj = _SelObject()
        self.open_targets = {}
        self.conn.connect(_SERVER_ADDR)
    
    def run(self):
        while True:
            data = self.conn.recv(1024)
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
            dic = json.loads(message)
            header = dic.pop('header')
            queue.put((header, dic))



"""
Utility methods - apply to both the client and server

Message format between client and server is (len1, len2, str1, str2). 
Normally first and second string represent (target, message). 
(target, "") from client to server means subscribe to target
"""


def _send_message(conn, target, msg):
    conn.sendall(len(target).to_bytes(4, "little"))
    conn.sendall(len(msg).to_bytes(4, "little"))
    conn.sendall(target.encode("utf-8"))
    conn.sendall(msg.encode("utf-8"))

class _SelObject:
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


"""
Server methods; apply to the LCM backend
The selector switches between each connection as data becomes availible;
this is simpler and more efficient than making threads for each connection
and creating a global lock for the subscriptions
"""

def _accept(sel, all_connections, sock):
    conn, addr = sock.accept()  # Should be ready
    print('accepted connection from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, _SelObject())
    all_connections.append(conn)

def _read(sel, all_connections, subscriptions, conn, obj):
    data = conn.recv(1024)  # Should be ready
    if len(data) == 0:
        print('closing connection from socket')
        sel.unregister(conn)
        conn.close()
        all_connections.remove(conn)
        for lst in subscriptions.values():
            while conn in lst:
                lst.remove(conn)
    else:
        obj.inb += data
        for target_channel, message in obj:
            subscriptions.setdefault(target_channel, [])
            if len(message) == 0:
                subscriptions[target_channel].append(conn)
            else:
                for c in subscriptions[target_channel]:
                    _send_message(c, target_channel, message)

def _start_backend():
    all_connections = []
    subscriptions = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(_SERVER_ADDR)
    sock.listen()
    sock.setblocking(False)
    sel = selectors.DefaultSelector()
    sel.register(sock, selectors.EVENT_READ, None)
    while True:
        events = sel.select(timeout=None)
        for key, _mask in events:
            if key.data is None:
                _accept(sel, all_connections, key.fileobj)
            else:
                _read(sel, all_connections, subscriptions, key.fileobj, key.data)

if __name__ == "__main__":
    print("Starting LCM server at address:", _SERVER_ADDR)
    _start_backend()
