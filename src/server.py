"""
server.py — The bridge between the browser UIs and the YDL message bus.

This Flask + Socket.IO web server does two jobs:
  1. Serves the HTML pages listed in UI_PAGES (scoreboard, staff GUI, etc.),
     enforcing a shared password on the staff-only pages.
  2. Translates messages between two worlds, in both directions:
       browser --socket.io 'ui-to-server'--> this server --YDL--> shepherd.py
       shepherd.py --YDL (target UI)--> this server --socket.io emit--> browser
     Every YDL message addressed to YDL_TARGETS.UI is broadcast to ALL
     connected browsers; each page's JS simply ignores headers it doesn't
     subscribe to.

This process holds no game state — it is a stateless relay.
Run with: python3 server.py  (pages served at http://localhost:5002/<page>)
"""
import json
import hashlib
import gevent
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from ydl import Client
from utils import YDL_TARGETS, UI_PAGES, CONSTANTS

HOST_URL = "127.0.0.1"
PORT = 5002

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")
YC = Client(YDL_TARGETS.UI)


@app.route('/')
def hello_world():
    return 'Hello, World!'


def password(p):
    """
    checks to make sure p is the correct password
    if you want to change the password, change the hash in utils.py
    """
    if p is None:
        return False
    m = hashlib.sha256()
    m.update((p + "cheese").encode("utf-8"))
    return m.hexdigest() == CONSTANTS.UI_PASSWORD_HASH


@app.route('/<path:subpath>')
def give_page(subpath):
    """
    routing for all ui pages. Gives "page not found" if
    the page isn't in UI_PAGES, or prompts for password
    if the page is password protected
    """
    if subpath[-1] == "/":
        subpath = subpath[:-1]
    if subpath in UI_PAGES:
        passed = (not UI_PAGES[subpath]) or password(
            request.cookies.get('password'))
        return render_template(subpath if passed else "password.html")
    # return "oops page not found"


@socketio.event
def connect():
    print('Established socketio connection')


@socketio.on('join')
def handle_join(client_name):
    print(f'confirmed join: {client_name}')


@socketio.on('ui-to-server')
def ui_to_server(p, header, args=None):
    """
    Browser -> Shepherd direction. UI JS emits ('ui-to-server', password,
    header_name, json_args); after checking the password, the message is
    re-sent onto YDL addressed to Shepherd.
    """
    if not password(p):
        return
    if args is None:
        YC.send((YDL_TARGETS.SHEPHERD, header, {}))
    else:
        YC.send((YDL_TARGETS.SHEPHERD, header, json.loads(args)))


def receiver():
    """
    Shepherd -> browser direction. Blocks on the YDL queue (in a thread pool
    so gevent's event loop isn't blocked) and rebroadcasts each message to
    every connected browser, using the YDL header name as the socket.io
    event name (e.g. UI_HEADER.SCORES becomes a 'scores' event).
    """
    tpool = gevent.get_hub().threadpool
    while True:
        event = tpool.spawn(YC.receive).get()  # event = (target, header, args)
        print("RECEIVED:", event[1], event[2])
        socketio.emit(event[1], json.dumps(event[2], ensure_ascii=False))


if __name__ == "__main__":
    print("Hello, world!")
    print(f"Running server on port {PORT}. Pages:")
    for page in UI_PAGES:
        print(f"\thttp://localhost:{PORT}/{page}")

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
