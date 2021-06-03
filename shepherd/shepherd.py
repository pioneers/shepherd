import argparse
import queue
import time
import traceback
import threading
from datetime import datetime
from alliance import Alliance
from ydl import ydl_send, ydl_start_read
from timer import Timer
from utils import *
from code import *
from protos.run_mode_pb2 import Mode
from runtimeclient import RuntimeClientManager
from protos.game_state_pb2 import State
from sheet import Sheet
from robot import Robot
from challenge_results import CHALLENGE_RESULTS

# pylint: disable=global-statement

CLIENTS = RuntimeClientManager()

###########################################
# Evergreen Variables
###########################################

GAME_STATE: str = STATE.END
GAME_TIMER = Timer(TIMER_TYPES.MATCH)
ROBOT = Robot("", -1, "")

MATCH_NUMBER = -1
ROUND_NUMBER = -1
ALLIANCES = {ALLIANCE_COLOR.GOLD: None, ALLIANCE_COLOR.BLUE: None}
EVENTS = None

LAST_HEADER = None

###########################################
# Game Specific Variables
###########################################
STARTING_SPOTS = ["unknown", "unknown", "unknown", "unknown"]
MASTER_ROBOTS = {ALLIANCE_COLOR.BLUE: None, ALLIANCE_COLOR.GOLD: None}

STUDENT_DECODE_TIMER = Timer(TIMER_TYPES.STUDENT_DECODE)
STOPLIGHT_TIMER = Timer(TIMER_TYPES.STOPLIGHT_WAIT)
SANDSTORM_TIMER = Timer(TIMER_TYPES.SANDSTORM_COVER)
DEHYDRATION_TIMER = Timer(TIMER_TYPES.DEHYDRATION)
ROBOT_DEHYDRATED_TIMER = Timer(TIMER_TYPES.ROBOT_DEHYDRATED)

CODES_USED = []

###########################################
# 2020 Game Specific Variables
###########################################
TINDER = 0
BUTTONS = Buttons()
FIRE_LIT = False
LAST_TINDER = 0
LAST_BUTTONS = Buttons()
LAST_FIRE_LIT = False

CHECKING_LINEBREAKS = False
LINEBREAK_HEADERS = [False] * 6

###########################################
# Evergreen Methods
###########################################

# pylint: disable=broad-except


def start():
    '''
    Main loop which processes the event queue and calls the appropriate function
    based on game state and the dictionary of available functions
    '''
    global LAST_HEADER
    global EVENTS
    global LINEBREAK_HEADERS
    EVENTS = queue.Queue()
    ydl_start_read(YDL_TARGETS.SHEPHERD, EVENTS)
    while True:
        print("GAME STATE OUTSIDE: ", GAME_STATE)
        time.sleep(0.1)
        payload = EVENTS.get(True)
        LAST_HEADER = payload
        print(payload)

        funcmappings = {
            STATE.SETUP: (SETUP_FUNCTIONS, "Setup"),
            STATE.AUTO: (AUTO_FUNCTIONS, "Auto"),
            STATE.TELEOP: (TELEOP_FUNCTIONS, "Teleop"),
            STATE.END: (END_FUNCTIONS, "End"),
        }

        if GAME_STATE in funcmappings:
            func_list, state_name = funcmappings.get(GAME_STATE)
            func = func_list.get(payload[0]) or EVERYWHERE_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in {0}".format(state_name))
        else:
            print("Invalid State: {}".format(GAME_STATE))



#pylint: disable=too-many-locals


def to_setup(args):
    '''
    Move to the setup stage which should push scores from previous game to spreadsheet,
    load the teams for the upcoming match, reset all state, and send information to scoreboard.
    By the end, should be ready to start match.
    '''
    global MATCH_NUMBER, ROUND_NUMBER
    global GAME_STATE
    global STARTING_SPOTS
    global ROBOT
    global BUTTONS
    global CLIENTS

    # code_setup()

    MATCH_NUMBER, ROUND_NUMBER = args["match_num"], args["round_num"]
    name, num = args["team_name"], args["team_num"]
    custom_ip = args.get("custom_ip", ROBOT.custom_ip)

    ROBOT = Robot(name, num, custom_ip)
    CLIENTS.reset()
    CLIENTS = RuntimeClientManager()
    connect()

    # note that reset state will be called from the UI when necessary and reset_state + reset_round = reset match
    reset_round()

    # so if there are other UIs open they get the update
    send_round_info()

    # turn on lasers
    ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LASERS, {})

    # YDL send to scoreboard about robot

    GAME_STATE = STATE.SETUP
    ydl_send(YDL_TARGETS.UI, UI_HEADER.STAGE, {"stage": GAME_STATE})
    print("ENTERING SETUP STATE")

    # turn stoplight red
    ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "red"})


def to_auto(args):
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    #pylint: disable= no-member
    global GAME_STATE, ROBOT
    global CLIENTS
    # CLIENTS.receive_all_challenge_data()

    GAME_TIMER.start_timer(CONSTANTS.AUTO_TIME)
    GAME_STATE = STATE.AUTO
    ROBOT.start_time = time.time()
    # STOPLIGHT_TIMER.start_timer(CONSTANTS.STOPLIGHT_TIME)
    ydl_send(YDL_TARGETS.UI,
             UI_HEADER.STAGE, {"stage": GAME_STATE, "start_time": ROBOT.start_time_millis()})
    send_score_to_ui()
    enable_robots(True)
    check_code()
    BUTTONS.illuminate_all()
    if TINDER > 0:
        ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_FIRE_LIGHT)

    print("ENTERING AUTO STATE")


def reset_round(args=None):
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global GAME_STATE, EVENTS, CLIENTS, ROBOT, TINDER, BUTTONS, FIRE_LIT
    GAME_STATE = STATE.SETUP
    Timer.reset_all()
    EVENTS = queue.Queue()
    ydl_start_read(YDL_TARGETS.SHEPHERD, EVENTS)
    ydl_send(YDL_TARGETS.UI, UI_HEADER.RESET_TIMERS)
    ydl_send(YDL_TARGETS.UI, UI_HEADER.SANDSTORM, {"on": False})
    CLIENTS.send_game_state(State.HYPOTHERMIA_END)
    ROBOT.reset()
    TINDER = LAST_TINDER
    BUTTONS = LAST_BUTTONS
    FIRE_LIT = LAST_FIRE_LIT
    """
    CLIENTS = RuntimeClientManager()
    """
    disable_robots()

    turn_off_all_lights()

    ydl_send(YDL_TARGETS.TABLET, TABLET_HEADER.RESET)
    ydl_send(YDL_TARGETS.DAWN, DAWN_HEADER.RESET)
    print("RESET MATCH, MOVE TO SETUP")


def reset_state(args):
    """
    This is called after a match is complete because tinder and buttons are persisted across rounds for the same alliance but not when the next alliance begins.
    """
    global TINDER, BUTTONS, FIRE_LIT
    TINDER = 0
    FIRE_LIT = False
    BUTTONS = Buttons()
    send_round_info()


def get_round(args):
    '''
    Retrieves all match info based on match number and sends this information to the UI. If not already cached, fetches info from the spreadsheet.
    '''
    global MATCH_NUMBER, ROUND_NUMBER, ROBOT, TINDER, BUTTONS
    match_num = int(args["match_num"])
    round_num = int(args["round_num"])

    # if robot info is for the correct match, round
    if not (MATCH_NUMBER == match_num and ROUND_NUMBER == round_num):
        MATCH_NUMBER = match_num
        ROUND_NUMBER = round_num
        try:
            info = Sheet.get_round(match_num, round_num)
            ROBOT.number = info["num"]
            ROBOT.name = info["name"]
        except Exception as e:
            print("Exception while reading from sheet:",e)
            info = {"num":-1, "name":""}

    send_round_info()
    

def send_round_info(args = None):
    '''
    Sends all match info to the UI and scoreboard
    '''
    global MATCH_NUMBER, ROUND_NUMBER, ROBOT, TINDER, BUTTONS
    team_num = ROBOT.number
    team_name = ROBOT.name
    ydl_data = {"match_num": MATCH_NUMBER, "round_num": ROUND_NUMBER,
                "team_num": team_num, "team_name": team_name, "custom_ip": ROBOT.custom_ip, "tinder": TINDER, "buttons": BUTTONS.illuminated}
    ydl_send(YDL_TARGETS.UI, UI_HEADER.TEAMS_INFO, ydl_data)

def get_biome(args):
    ydl_send(YDL_TARGETS.UI, UI_HEADER.STAGE, {"stage": GAME_STATE})

def set_biome(args):
    biome = args["biome"]
    state_to_transition_function = {
        STATE.CITY: city_linebreak,
        STATE.SANDSTORM: to_desert,
        STATE.DEHYDRATION: to_dehydration,
        STATE.HYPOTHERMIA: to_hypothermia,
        STATE.FINAL: to_final,
        STATE.END: to_end
    }
    if biome not in state_to_transition_function:
        print(f"Sorry, {biome} is not a valid state to move to.")
        return
    state_to_transition_function[biome]({})

def set_custom_ip(args):
    ROBOT.custom_ip = args["custom_ip"]
    connect()

def connect():
    CLIENTS.get_clients([ROBOT.custom_ip], [ROBOT])

def send_connection_status_to_ui(args = None):
    '''
    Sends the connection status of all runtime clients to the UI
    '''
    CLIENTS.send_connection_status_to_ui()

def score_adjust(args):
    '''
    Allow for score to be changed based on referee decisions
    '''
    global GAME_STATE
    time, penalty, stamp_time = args.get("time"), args.get(
        "penalty"), args.get("stamp_time")
    if GAME_STATE == STATE.END or GAME_STATE == STATE.SETUP:
        if time is not None:
            ROBOT.set_elapsed_time(time)
    if penalty is not None:
        ROBOT.penalty = penalty
    if stamp_time is not None:
        ROBOT.stamp_time = stamp_time
    send_score_to_ui()
    flush_scores()

def send_score_to_ui(args = None):
    '''
    Send the current score to the UI.
    '''
    data = {
        "time": ROBOT.elapsed_time(),
        "penalty": ROBOT.penalty,
        "stamp_time": ROBOT.stamp_time,
        "score": ROBOT.total_time(),
        "start_time": ROBOT.start_time_millis()
    }
    ydl_send(YDL_TARGETS.UI, UI_HEADER.SCORES, data)


def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    try:
        Sheet.write_scores(MATCH_NUMBER, ROUND_NUMBER, ROBOT.total_time())
    except Exception as e:
        print(f"Unable to push scores to spreadsheet: {e}")


def enable_robots(autonomous):
    '''
    Sends message to Runtime to enable all robots. The argument should be a boolean
    which is true if we are entering autonomous mode
    '''
    CLIENTS.send_mode(Mode.AUTO if autonomous else Mode.TELEOP)


def disable_robots():
    '''
    Sends message to Dawn to disable all robots
    '''
    CLIENTS.send_mode(Mode.IDLE)

#pylint: disable=redefined-builtin

def log(msg):
    print("haha log")
    print(msg)


###########################################
# Game Specific Methods
###########################################


def disable_robot(args):
    '''
    Send message to Dawn to disable the robot of team
    '''
    disable_robots() #hotfix, no idea why other doesn't work
    #send_robot_mode(int(args["team_number"]), Mode.IDLE)

def enable_robot(args):
    '''
    Send message to Dawn to enable the robot of team
    '''
    enable_robots(GAME_STATE == STATE.AUTO) #hotfix, no idea why other doesn't work
    #mode = Mode.AUTO if GAME_STATE == STATE.AUTO else Mode.TELEOP
    #send_robot_mode(int(args["team_number"]), mode)

def send_robot_mode(team_number, mode):
    try:
        for client in CLIENTS.clients:
            if client.robot.number == team_number:
                client.send_mode(mode)
    except Exception as exc:
        log(exc)


def set_game_info(args):
    '''
    Set tinder/buttons from UI. If tinder/buttons are not passed in, they are ignored.
    If in end state, LAST_TINDER is also set for the next round. TINDER is always set
    because it could be done by the referee.
    '''
    global TINDER, LAST_TINDER
    if args.get("tinder", ""):
        TINDER = int(args["tinder"])
        if GAME_STATE == STATE.END:
            LAST_TINDER = TINDER
    if args.get("buttons", ""):
        BUTTONS.illuminated = int(args["buttons"])
        if GAME_STATE == STATE.END:
            LAST_BUTTONS.illuminated = BUTTONS.illuminated
    print(f"Current Tinder: {TINDER}")
    print(f"Current num buttons: {BUTTONS.illuminated}")


###########################################
# Spring 2020 Game
###########################################






def to_end(args):
    '''
    Go to the end state.
    '''
    global GAME_STATE
    GAME_STATE = STATE.END
    disable_robots()
    CLIENTS.reset()
    GAME_TIMER.reset()
    # ROBOT.end_time = time.time() #TODO: keep?
    GAME_STATE = STATE.END
    send_score_to_ui()
    ydl_send(YDL_TARGETS.UI, UI_HEADER.STAGE, {"stage": GAME_STATE})

    flush_scores()



# TODO: someone would have to read headers to figure out which linebreaks were not working


###########################################
# Event to Function Mappings for each Stage
###########################################
SETUP_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_auto,
    SHEPHERD_HEADER.SET_GAME_INFO: set_game_info,
    SHEPHERD_HEADER.RESET_MATCH: reset_state,
    SHEPHERD_HEADER.GET_MATCH_INFO: to_setup
}

AUTO_FUNCTIONS = {
    SHEPHERD_HEADER.STAGE_TIMER_END: to_teleop
}

TELEOP_FUNCTIONS = {
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end
}

END_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.GET_ROUND_INFO: get_round,
    SHEPHERD_HEADER.FINAL_SCORE: final_score,
    SHEPHERD_HEADER.SET_GAME_INFO: set_game_info,
    SHEPHERD_HEADER.SET_CUSTOM_IP: set_custom_ip,
    SHEPHERD_HEADER.RESET_MATCH: reset_state,
}

EVERYWHERE_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.ROBOT_ON: enable_robot,
    SHEPHERD_HEADER.GET_MATCH_INFO_NO_ARGS: send_round_info,
    SHEPHERD_HEADER.GET_SCORES: send_score_to_ui,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connection_status_to_ui,
    SHEPHERD_HEADER.SCORE_ADJUST: score_adjust,
    SHEPHERD_HEADER.SET_CUSTOM_IP: set_custom_ip,
}


if __name__ == '__main__':
    start()
