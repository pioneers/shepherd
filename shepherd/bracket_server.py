import Sheet
import json
from flask import Flask, render_template  # pylint: disable=import-error
from flask_socketio import SocketIO, emit, join_room, leave_room, send  # pylint: disable=import-errors

HOST_URL = "0.0.0.0"
PORT = 5100

app = Flask(__name__)

app.config['SECRET_KEY'] = 'omegalul!'
socketio = SocketIO(app, async_mode="gevent")

"""
- 8 seeds
- On refresh want who played and who won (current state)
"""
@app.route('/')
def hello_world():
    return render_template('bracket.html')
    # return 'Hello, World!'




# Score Adjustment

@socketio.on('all-info')
def all_info():
    """
    goal: get the 8 seeds and the list of matches played and who won
    returns: {
        rankings: [teamA, teamB, ..., teamH],
        
    }
    """
    # lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.GET_SCORES)
    pass



def receiver():
   
    while True:
           
        socketio.emit('server-to-ui-teams-info', json.dumps({}, ensure_ascii=False))
        socketio.sleep(0.1)

if __name__ == "__main__":
    print("Hello, world!")
    print(f"Running server on port {PORT}. Go to http://localhost:{PORT}/")

socketio.start_background_task(receiver)
socketio.run(app, host=HOST_URL, port=PORT)