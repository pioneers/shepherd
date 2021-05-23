import json
import queue
import hashlib
from flask import Flask, render_template, request  # pylint: disable=import-error
from flask_socketio import SocketIO  # pylint: disable=import-errors
from shepherd.core.Utils import LCM_TARGETS
from shepherd.core.LCM import lcm_send, lcm_start_read

HOST_URL = "0.0.0.0"
PORT = 5000

app = Flask(__name__, 
    template_folder='../templates', 
    static_folder='../static')
app.config['SECRET_KEY'] = 'omegalul!'
app.config['TEMPLATES_AUTO_RELOAD'] = True
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")


@app.route('/')
def hello_world():
    return 'Hello, World!'

def password(p):
    if p is None:
        return False
    m = hashlib.sha256()
    m.update((p + "cheese").encode("utf-8"))
    return m.hexdigest() == \
        "44590c963be2a79f52c07f7a7572b3907bf5bb180d993bd31aab510d29bbfbd3"

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
        if password(request.cookies.get('password')):
            return render_template(subpath)
        else:
            return render_template("password.html")
    else:
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
        lcm_send(LCM_TARGETS.SHEPHERD, header)
    else:
        lcm_send(LCM_TARGETS.SHEPHERD, header, json.loads(args))
        

def receiver():
    events = queue.Queue()
    lcm_start_read(LCM_TARGETS.UI, events)
    while True:
        if not events.empty():
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