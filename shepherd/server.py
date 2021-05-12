import json
import threading
import time
import queue
import gevent  # pylint: disable=import-error
from flask import Flask, render_template  # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send  # pylint: disable=import-errors
from Utils import LCM_TARGETS, SHEPHERD_HEADER, UI_HEADER
from LCM import lcm_send, lcm_start_read

HOST_URL = "0.0.0.0"
PORT = 5000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/<path:subpath>')
def give_page(subpath):
    if subpath[-1] == "/":
        subpath = subpath[:-1] 
    if subpath in [
        "score_adjustment.html",
        "staff_gui.html",
        "stage_control.html",
        "ref_gui.html",
        "scoreboard.html"
    ]:
        return render_template(subpath)
    else:
        return "oops page not found"

@socketio.event
def connect():
    print('Established socketio connection')

@socketio.on('join')
def handle_join(client_name):
    print(f'confirmed join: {client_name}')
    join_room(client_name)

@socketio.on('ui-to-server')
def ui_to_server(header, args=None):
    if args is None:
        lcm_send(LCM_TARGETS.SHEPHERD, header)
    else:
        lcm_send(LCM_TARGETS.SHEPHERD, header, json.loads(args))
        

def receiver():
    ui_events = gevent.queue.Queue()
    scoreboard_events = gevent.queue.Queue()
    lcm_start_read(LCM_TARGETS.UI, ui_events)
    lcm_start_read(LCM_TARGETS.SCOREBOARD, scoreboard_events)

    while True:
        if not ui_events.empty():
            event = ui_events.get_nowait()
            print("UI RECEIVED:", event)
            socketio.emit(event[0], json.dumps(event[1], ensure_ascii=False), to="ui")
        if not scoreboard_events.empty():
            event = scoreboard_events.get_nowait()
            print("SCOREBOARD RECEIVED:", event)
            socketio.emit(event[0], json.dumps(event[1], ensure_ascii=False), to="scoreboard")
        socketio.sleep(0.1)

if __name__ == "__main__":
    print("Hello, world!")
    print(f"Running server on port {PORT}.",
        f"Go to http://localhost:{PORT}/staff_gui.html",
        f"or http://localhost:{PORT}/scoreboard.html")

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)