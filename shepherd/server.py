import json
import threading
import time
import queue
import gevent  # pylint: disable=import-error
from flask import Flask, render_template  # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send  # pylint: disable=import-error
from Utils import *
from LCM import *

HOST_URL = "0.0.0.0"
PORT = 5000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app, async_mode="gevent")


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/score_adjustment.html/')
def score_adjustment():
    return render_template('score_adjustment.html')


@app.route('/staff_gui.html/')
def staff_gui():
    return render_template('staff_gui.html')


@app.route('/stage_control.html/')
def stage_control():
    return render_template('stage_control.html')

@app.route('/ref_gui.html/')
def ref_gui():
    return render_template('ref_gui.html')


@socketio.on('join')
def handle_join(client_name):
    print('confirmed join: ' + client_name)
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.REQUEST_CONNECTIONS)

# Score Adjustment


@socketio.on('ui-to-server-scores')
def ui_to_server_scores(scores):
    lcm_send(LCM_TARGETS.SHEPHERD,
             SHEPHERD_HEADER.SCORE_ADJUST, json.loads(scores))


@socketio.on('ui-to-server-score-request')
def ui_to_server_score_request():
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GET_SCORES)


# Main GUI

@socketio.on('ui-to-server-teams-info-request-no-args')
def ui_to_server_round_info_request_no_args():
    print("TEAMS Info request on load made")
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GET_ROUND_INFO_NO_ARGS)

@socketio.on('ui-to-server-teams-info-request')
def ui_to_server_round_info_request(round_info):
    print("TEAMS Info request made")
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GET_ROUND_INFO,
            json.loads(round_info))

@socketio.on('ui-to-server-setup-match')
def ui_to_server_setup_match(teams_info):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.SETUP_MATCH,
             json.loads(teams_info))

@socketio.on('ui-to-server-start-next-stage')
def ui_to_server_start_next_stage():
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.START_NEXT_STAGE)

@socketio.on('ui-to-server-reset-match')
def ui_to_server_reset_match():
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.RESET_MATCH)

@socketio.on('ui-to-server-reset-round')
def ui_to_server_reset_round():
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.RESET_ROUND)

@socketio.on('ui-to-server-game-info')
def ui_to_server_game_info(game_info):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.SET_GAME_INFO,
             json.loads(game_info))

@socketio.on('ui-to-server-set-tinder')
def ui_to_server_set_tinder(args):
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.SET_TINDER, json.loads(args))

@socketio.on('ui-to-server-custom-ip')
def ui_to_server_custom_ip(args):
    lcm_send(LCM_TARGETS.SHEPHERD, 
             SHEPHERD_HEADER.SET_CUSTOM_IP, json.loads(args))

#Ref GUI buttons

@socketio.on('ui-to-server-contact-wall')
def ui_to_server_contact_wall():
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.CONTACT_WALL)

@socketio.on('ui-to-server-drawbridge-shortcut')
def ui_to_server_drawbridge_shortcut():
    lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.DRAWBRIDGE_SHORTCUT)


def receiver():
    events = gevent.queue.Queue()
    lcm_start_read(str.encode(LCM_TARGETS.UI), events)

    while True:

        if not events.empty():
            event = events.get_nowait()
            print("RECEIVED:", event)
            if event[0] == UI_HEADER.TEAMS_INFO:
                socketio.emit('server-to-ui-teams-info',
                              json.dumps(event[1], ensure_ascii=False))
            elif event[0] == UI_HEADER.SCORES:
                socketio.emit('server-to-ui-scores',
                              json.dumps(event[1], ensure_ascii=False))
        socketio.sleep(0.1)


socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)
