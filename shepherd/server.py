import json
import queue
import hashlib
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from utils import YDL_TARGETS, UI_PAGES
from ydl import ydl_send, ydl_start_read

HOST_URL = "0.0.0.0"
PORT = 5000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")


@app.route('/')
def hello_world():
    return 'Hello, World!'


"""
checks to make sure p is the correct password
if you want to change the password, just change the hash
"""
def password(p):
    if p is None:
        return False
    m = hashlib.sha256()
    m.update((p + "cheese").encode("utf-8"))
    return m.hexdigest() == \
        "44590c963be2a79f52c07f7a7572b3907bf5bb180d993bd31aab510d29bbfbd3"

"""
routing for all ui pages. Gives "page not found" if
the page isn't in UI_PAGES, or prompts for password 
if the page is password protected
"""
@app.route('/<path:subpath>')
def give_page(subpath):
    if subpath[-1] == "/":
        subpath = subpath[:-1]
    if subpath in UI_PAGES:
        passed = (not UI_PAGES[subpath]) or password(request.cookies.get('password'))
        return render_template(subpath if passed else "password.html")
    return "oops page not found"

@socketio.event
def connect():
    print('Established socketio connection')

@socketio.on('join')
def handle_join(client_name):
    print(f'confirmed join: {client_name}')

@socketio.on('ui-to-server')
def ui_to_server(p, header, args=None):
    if not password(p):
        return
    if args is None:
        ydl_send(YDL_TARGETS.SHEPHERD, header)
    else:
        ydl_send(YDL_TARGETS.SHEPHERD, header, json.loads(args))


def receiver():
    events = queue.Queue()
    ydl_start_read(YDL_TARGETS.UI, events)
    while True:
        while not events.empty():
            event = events.get()
            print("RECEIVED:", event)
            socketio.emit(event[0], json.dumps(event[1], ensure_ascii=False))
        socketio.sleep(0.1)

if __name__ == "__main__":
    print("Hello, world!")
    print(f"Running server on port {PORT}.",
        f"Go to http://localhost:{PORT}/staff_gui.html",
        f"or http://localhost:{PORT}/scoreboard.html")

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
