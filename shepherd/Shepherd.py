import argparse
import queue
import time
import traceback
from datetime import datetime
from Utils import SHEPHERD_HEADER
from Alliance import *
from LCM import *
from Timer import Timer
from Utils import *
from Code import * 
# TODO: import protos and change things like "auto" to Mode.AUTO
from protos.run_mode_pb2 import Mode
from runtimeclient import RuntimeClientManager
from protos.game_state_pb2 import State
import Sheet
import bot
import audio
from Robot import Robot
from Buttons import Buttons
from challenge_results import CHALLENGE_RESULTS

# pylint: disable=global-statement

CLIENTS = RuntimeClientManager()

__version__ = (1, 0, 0)

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
    EVENTS = queue.Queue()
    lcm_start_read(LCM_TARGETS.SHEPHERD, EVENTS)
    while True:
        print("GAME STATE OUTSIDE: ", GAME_STATE)
        time.sleep(0.1)
        payload = EVENTS.get(True)
        LAST_HEADER = payload
        print(payload)

        funcmappings = {
            STATE.SETUP: (SETUP_FUNCTIONS, "Setup"),
            STATE.AUTO: (AUTO_FUNCTIONS, "Auto"),
            STATE.CITY: (CITY_FUNCTIONS, "City"),
            STATE.SANDSTORM: (SANDSTORM_FUNCTIONS, "Sandstorm"),
            STATE.DEHYDRATION: (DEHYDRATION_FUNCTIONS, "Dehydration"),
            STATE.FIRE: (FIRE_FUNCTIONS, "Fire"),
            STATE.HYPOTHERMIA: (HYPOTHERMIA_FUNCTIONS, "Hypothermia"),
            STATE.FINAL: (FINAL_FUNCTIONS, "Final"),
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
    global MATCH_NUMBER
    global GAME_STATE
    global STARTING_SPOTS
    global ROBOT
    global BUTTONS
    global CLIENTS

    # code_setup()

    name, num = args["team_name"], args["team_num"]
    custom_ip = args.get("custom_ip", ROBOT.custom_ip)

    ROBOT = Robot(name, num, custom_ip)
    CLIENTS = RuntimeClientManager()
    connect()

    # note that reset state will be called from the UI when necessary and reset_state + reset_round = reset match
    reset_round()

    # so if there are other UIs open they get the update
    send_round_info()

    # turn on lasers
    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LASERS, {})

    # LCM send to scoreboard about robot

    GAME_STATE = STATE.SETUP
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    print("ENTERING SETUP STATE")

    # turn stoplight red
    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "red"})


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
    STOPLIGHT_TIMER.start_timer(CONSTANTS.STOPLIGHT_TIME)
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE, "start_time": ROBOT.start_time_millis()})
    lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.AUTO})
    send_score_to_ui()
    enable_robots(True)
    check_code()

    BUTTONS.illuminate_buttons()
    BUTTONS.randomize_correct_button()
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
    lcm_start_read(LCM_TARGETS.SHEPHERD, EVENTS)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.RESET_TIMERS)
    ROBOT.reset()
    TINDER = LAST_TINDER
    BUTTONS = LAST_BUTTONS
    FIRE_LIT = LAST_FIRE_LIT
    """
    CLIENTS = RuntimeClientManager()
    """
    disable_robots()

    turn_off_all_lights()

    lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.RESET)
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.RESET)
    print("RESET MATCH, MOVE TO SETUP")


def reset_state(args):
    """
    This is called after a match is complete because tinder and buttons are persisted across rounds for the same alliance but not when the next alliance begins.
    """
    global TINDER, BUTTONS, FIRE_LIT
    TINDER = 0
    FIRE_LIT = False
    BUTTONS = Buttons()


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
        except Exception as e:
            print("Exception while reading from sheet:",e)
            info = {"num":-1, "name":""}
        ROBOT.number = info["num"]
        ROBOT.name = info["name"]

    send_round_info()
    

def send_round_info(args = None):
    '''
    Sends all match info to the UI and scoreboard
    '''
    global MATCH_NUMBER, ROUND_NUMBER, ROBOT, TINDER, BUTTONS
    team_num = ROBOT.number
    team_name = ROBOT.name
    lcm_data = {"match_num": MATCH_NUMBER, "round_num": ROUND_NUMBER,
                "team_num": team_num, "team_name": team_name, "custom_ip": ROBOT.custom_ip, "tinder": TINDER, "buttons": BUTTONS.illuminated}
    lcm_send(LCM_TARGETS.UI, UI_HEADER.TEAMS_INFO, lcm_data)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.TEAM, {"team_num": team_num, "team_name": team_name})

def get_biome(args):
    lcm_send(LCM_TARGETS.UI, UI_HEADER.BIOME, {"biome": GAME_STATE})

def set_biome(args):
    biome = args["biome"]
    state_to_transition_function = {
        STATE.CITY: to_city,
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
    # TODO: send dummy elapsed time if during game (-1) maybe this should be none
    send_score_to_scoreboard()
    send_score_to_ui()

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
    lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES, data)

def send_score_to_scoreboard(args=None):
    """
    Send the current score to the scoreboard.
    """
    data = {
        "time": ROBOT.elapsed_time(),
        "penalty": ROBOT.penalty,
        "stamp_time": ROBOT.stamp_time,
        "score": ROBOT.total_time(),
        "start_time": ROBOT.start_time_millis()
    }
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORES, data)

def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    Sheet.write_scores(MATCH_NUMBER, ROUND_NUMBER, ROBOT.total_time())
    return -1


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


def log(Exception):
    global LAST_HEADER
    # if Shepherd.MATCH_NUMBER <= 0:
    #     return
    now = datetime.now()
    filename = str(now.month) + "-" + str(now.day) + "-" + str(now.year) +\
        "-match-" + str(MATCH_NUMBER) + ".txt"
    print("a normally fatal exception occured, but Shepherd will continue to run")
    print("all known details are logged to logs/"+filename)
    file = open("logs/"+filename, "a+")
    file.write("\n========================================\n")
    file.write("a normally fatal exception occured.\n")
    file.write("all relevant data may be found below.\n")
    file.write("match: " + str(MATCH_NUMBER)+"\n")
    file.write("game state: " + str(GAME_STATE)+"\n")
    file.write("robot: " + str(ROBOT)+"\n")
    file.write("game timer running?: " + str(GAME_TIMER.is_running())+"\n")
    file.write("the last received header was:" + str(LAST_HEADER)+"\n")
    file.write("a stacktrace of the error may be found below\n")
    file.write(str(Exception))
    file.write(str(traceback.format_exc()))
    file.close()

###########################################
# Game Specific Methods
###########################################


def disable_robot(args):
    '''
    Send message to Dawn to disable the robot of team
    '''
    try:
        team_number = args["team_number"]
        client = CLIENTS.clients[int(team_number)]
        if client:
            client.send_mode(Mode.IDLE)
    except Exception as exc:
        log(exc)

def enable_robot(args):
    '''
    Send message to Dawn to enable the robot of team
    '''
    mode = Mode.AUTO if GAME_STATE == STATE.AUTO else Mode.TELEOP
    try:
        team_number = args["team_number"]
        client = CLIENTS.clients[int(team_number)]
        if client:
            client.send_mode(mode)
    except Exception as exc:
        log(exc)


def final_score(args):
    '''
    send shepherd the final score, send score to scoreboard
    '''
    send_score_to_scoreboard()


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

# ----------
# SETUP STAGE
# ----------

def check_code():
    '''
    Check the coding challenges and act appropriately
    '''
    ROBOT.coding_challenge = CHALLENGE_RESULTS[ROBOT.number]

# ----------
# AUTO STAGE
# ----------


def to_city(args):
    '''
    Go to the city stage
    '''
    global GAME_STATE
    enable_robots(autonomous=False)
    curr_time = time.time() - ROBOT.start_time
    GAME_TIMER.reset()
    GAME_TIMER.start_timer(CONSTANTS.TOTAL_TIME - curr_time)
    GAME_STATE = STATE.CITY
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE, "start_time": ROBOT.start_time_millis()})
    lcm_send(LCM_TARGETS.UI, UI_HEADER.STAGE, {
             "stage": GAME_STATE, "start_time": ROBOT.start_time_millis()})
    lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.CITY})
    print("ENTERING CITY STATE")

# ----------
# CITY STAGE
# ----------


def stoplight_timer_end(args):
    # turn stoplight green
    STOPLIGHT_TIMER.reset()
    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "green"})


def stoplight_button_press(args):
    '''
    Triggered by a press of the stoplight button
    '''
    if ROBOT.pass_coding_challenges(n=1, tier=2):
        stoplight_timer_end([])
    
def stoplight_cross(args):
    # stoplight is not green
    if STOPLIGHT_TIMER.is_running():
        stoplight_penalty()


def stoplight_penalty():
    # whatever the penalty is
    ROBOT.penalty += CONSTANTS.STOPLIGHT_PENALTY
    send_score_to_scoreboard()
    send_score_to_ui()


def contact_wall(args):
    '''
    Triggered when the robot hits the wall
    '''
    CLIENTS.send_game_state(State.POISON_IVY)


def to_desert(args):
    '''
    Go to the sandstorm stage
    '''
    global GAME_STATE
    GAME_STATE = STATE.SANDSTORM
    lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.SANDSTORM})
    if ROBOT.pass_coding_challenges(n=1, tier=2) == 0:
        SANDSTORM_TIMER.start_timer(CONSTANTS.SANDSTORM_COVER_TIME)
        lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SANDSTORM, {"on": True})

# ----------
# SANDSTORM STAGE
# ----------


def sandstorm_timer_end(args):
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SANDSTORM, {"on": False})


def to_dehydration(args):
    '''
    Go to the dehydration stage
    '''
    global GAME_STATE
    GAME_STATE = STATE.DEHYDRATION
    lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.DEHYDRATION})
    DEHYDRATION_TIMER.start_timer(CONSTANTS.DEHYRATION_TIME)

# ----------
# DEHYDRATION STAGE
# ----------


def dehydration_button_press(args):
    '''
    Triggered when dehydration button is pressed
    '''
    global GAME_STATE
    button_number = int(args["button"])
    if BUTTONS.press_button_and_check(button_number, ROBOT):
        DEHYDRATION_TIMER.reset()  # stop dehydration timer so it doesn't run out
        GAME_STATE = STATE.FIRE
        lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.FIRE})


def dehydration_penalty_timer_start(args):
    '''
    Triggered when robot gets dehydrated ("water getting" timer runs out). Starts the penalty timer and forcibly stops the robot.
    '''
    ROBOT_DEHYDRATED_TIMER.start_timer(CONSTANTS.ROBOT_DEHYDRATED_TIME)
    CLIENTS.send_game_state(State.DEHYDRATION)


def dehydration_penalty_timer_end(args):
    '''
    Triggered when robot dehydration ends.
    '''
    global GAME_STATE
    GAME_STATE = STATE.FIRE


# ----------
# FIRE STAGE
# ----------

def set_tinder(args):
    '''
    This method sets the total amount of tinder
    1 tinder = fire is lit for one round.
    2 tinder = fire is lit for two rounds.
    3 tinder = fire is lit for three rounds.
    '''
    global TINDER
    TINDER = args["tinder"]
    send_round_info()


def fire_lever(args):
    '''
    Toggle the fire.
    '''
    global FIRE_LIT
    FIRE_LIT = True # this just means the lever was flipped.
    if TINDER > 0:
        lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_FIRE_LIGHT)

def to_hypothermia(args):
    '''
    Go to the hypothermia zone in the forest biome.
    '''
    global GAME_STATE, FIRE_LIT, TINDER
    GAME_STATE = STATE.HYPOTHERMIA
    lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.HYPOTHERMIA})

    if not (FIRE_LIT and TINDER > 0):
        CLIENTS.send_game_state(State.HYPOTHERMIA_START)
    elif FIRE_LIT and TINDER > 0:
        TINDER -= 1

# ----------
# HYPOTHERMIA STAGE
# ----------


def to_final(args):
    '''
    Go to the airport stage.
    '''
    global GAME_STATE
    GAME_STATE = STATE.FINAL
    lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.FINAL})
    CLIENTS.send_game_state(State.HYPOTHERMIA_END)

# ----------
# AIRPORT STAGE
# ----------


def to_end(args):
    '''
    Go to the end state.
    '''
    global GAME_STATE, LAST_TINDER, LAST_BUTTONS, LAST_FIRE_LIT
    LAST_TINDER = TINDER
    LAST_BUTTONS = BUTTONS.copy()
    LAST_FIRE_LIT = FIRE_LIT
    GAME_STATE = STATE.END
    lcm_send(LCM_TARGETS.UI,
             UI_HEADER.BIOME, {"biome": STATE.END})
    disable_robots()
    CLIENTS.reset()
    GAME_TIMER.reset()
    ROBOT.end_time = time.time()
    GAME_STATE = STATE.END
    send_score_to_ui()
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    send_score_to_scoreboard()
    lcm_send(LCM_TARGETS.UI, UI_HEADER.STAGE, {"stage": GAME_STATE})

    turn_off_all_lights()

    try:
        flush_scores()
    except Exception as e:
        print(f"Unable to push scores to spreadsheet: {e}")

def turn_off_all_lights():
    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_TRAFFIC_LIGHT)
    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_FIRE_LIGHT)
    lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LASERS, {})
    for i in range(Buttons.NUM_BUTTONS):
        lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {"id": i})
###########################################
# Event to Function Mappings for each Stage
###########################################
SETUP_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_auto,
    SHEPHERD_HEADER.SET_GAME_INFO: set_game_info,
    SHEPHERD_HEADER.SET_CUSTOM_IP: set_custom_ip,
    SHEPHERD_HEADER.RESET_MATCH: reset_state
}

AUTO_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STOPLIGHT_TIMER_END: stoplight_timer_end,
    SHEPHERD_HEADER.CITY_LINEBREAK: to_city, # line break sensor entering city
    SHEPHERD_HEADER.STAGE_TIMER_END: to_city # 20 seconds
}

# This represents City and Forest, since we don't need to detect Forest explicitly
CITY_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.STOPLIGHT_TIMER_END: stoplight_timer_end,
    SHEPHERD_HEADER.STOPLIGHT_BUTTON_PRESS: stoplight_button_press, # momentary switch
    SHEPHERD_HEADER.STOPLIGHT_PENALTY: stoplight_penalty,
    SHEPHERD_HEADER.STOPLIGHT_CROSS: stoplight_cross,
    SHEPHERD_HEADER.CONTACT_WALL: contact_wall,
    SHEPHERD_HEADER.DESERT_ENTRY: to_desert # triggered by line break sensor
}

SANDSTORM_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.DEHYDRATION_ENTRY: to_dehydration, # triggered by line break sensor
    SHEPHERD_HEADER.SANDSTORM_TIMER_END: sandstorm_timer_end
}

DEHYDRATION_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.DEHYDRATION_BUTTON_PRESS: dehydration_button_press,
    SHEPHERD_HEADER.DEHYDRATION_TIMER_END: dehydration_penalty_timer_start,
    SHEPHERD_HEADER.ROBOT_DEHYDRATED_TIMER_END: dehydration_penalty_timer_end,
    SHEPHERD_HEADER.SANDSTORM_TIMER_END: sandstorm_timer_end
}

FIRE_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.SET_TINDER: set_tinder,
    SHEPHERD_HEADER.FIRE_LEVER: fire_lever, # triggered by sensor
    SHEPHERD_HEADER.HYPOTHERMIA_ENTRY: to_hypothermia, # triggered by line break
    SHEPHERD_HEADER.SANDSTORM_TIMER_END: sandstorm_timer_end
}

HYPOTHERMIA_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end, 
    SHEPHERD_HEADER.FINAL_ENTRY: to_final # triggered by line break
}

FINAL_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.CITY_LINEBREAK: to_end # triggered by line break
}

END_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.GET_ROUND_INFO: get_round,
    SHEPHERD_HEADER.FINAL_SCORE: final_score,
    SHEPHERD_HEADER.SET_GAME_INFO: set_game_info,
    SHEPHERD_HEADER.RESET_MATCH: reset_state
}

EVERYWHERE_FUNCTIONS = {
    SHEPHERD_HEADER.GET_BIOME: get_biome,
    SHEPHERD_HEADER.SET_BIOME: set_biome,
    SHEPHERD_HEADER.GET_ROUND_INFO_NO_ARGS: send_round_info,
    SHEPHERD_HEADER.GET_SCORES: send_score_to_ui,
    SHEPHERD_HEADER.SCORE_ADJUST: score_adjust,
    SHEPHERD_HEADER.RESET_ROUND: reset_round
}


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='PiE field control')
    parser.add_argument('--version', help='Prints out the Shepherd version number.',
                        action='store_true')
    flags = parser.parse_args()

    if flags.version:
        print('.'.join(map(str, __version__)))
    else:
        start()


if __name__ == '__main__':
    main()
