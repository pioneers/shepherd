import json
import threading
import time
import queue
import gevent # pylint: disable=import-error
from flask import Flask, render_template # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send # pylint: disable=import-error
from Utils import *
from LCM import *

HOST_URL = "127.0.0.1"
PORT = 5500

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app, async_mode="gevent")

@app.route('/')
def hello_world():
    return 'Go to /scoreboard.html'

@app.route('/scoreboard.html/')
def scoreboard():
    return render_template('scoreboard.html')

def receiver():
    events = gevent.queue.Queue()
    lcm_start_read(str.encode(LCM_TARGETS.SCOREBOARD), events)

    while True:

        if not events.empty():
            event = events.get_nowait()
            print("RECEIVED:", event)
            if event[0] == SCOREBOARD_HEADER.SCORES:
                socketio.emit('score', json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.TEAM:
                socketio.emit('team', json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.STAGE:
                socketio.emit('stage', json.dumps(event[1], ensure_ascii=False))
            elif event[0] == SCOREBOARD_HEADER.RESET_TIMERS:
                socketio.emit('reset_timers', json.dumps(event[1], ensure_ascii=False))
        socketio.sleep(0.1)

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
