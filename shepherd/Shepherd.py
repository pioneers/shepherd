import argparse
import queue
import time
import traceback
from datetime import datetime
from Utils import SHEPHERD_HEADER
from Alliance import *
from LCM import *
from Timer import *
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
            STATE.FOREST: (FOREST_FUNCTIONS, "Forest"),
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

    # code_setup()

    name, num = args["team_name"], args["team_num"]
    custom_ip = args.get("custom_ip", ROBOT.custom_ip)

    ROBOT = Robot(name, num, custom_ip)
    BUTTONS = Buttons()

    # note that reset state will be called from the UI when necessary and reset_state + reset_round = reset match
    reset_round()

    # LCM send to scoreboard about robot

    GAME_STATE = STATE.SETUP
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    print("ENTERING SETUP STATE")


def to_auto(args):
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    #pylint: disable= no-member
    global GAME_STATE, ROBOT
    global CLIENTS
    try:
        CLIENTS = RuntimeClientManager()
        CLIENTS.get_clients([ROBOT.custom_ip], [ROBOT])
    except Exception as exc:
        log(exc)
        return
    CLIENTS.receive_all_challenge_data()

    GAME_TIMER.start_timer(CONSTANTS.AUTO_TIME)
    GAME_STATE = STATE.AUTO
    ROBOT.start_time = time.time()
    STOPLIGHT_TIMER.start_timer(CONSTANTS.STOPLIGHT_TIME)
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE, "start_time": ROBOT.start_time_millis()})
    lcm_send(LCM_TARGETS.UI, UI_HEADER.STAGE, {
             "stage": GAME_STATE, "start_time": ROBOT.start_time_millis()})
    enable_robots(True)

    BUTTONS.illuminate_buttons(ROBOT)
    print("ENTERING AUTO STATE")


def reset_round(args=None):
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global GAME_STATE, EVENTS, CLIENTS, ROBOT, TINDER, BUTTONS
    GAME_STATE = STATE.SETUP
    Timer.reset_all()
    EVENTS = queue.Queue()
    lcm_start_read(LCM_TARGETS.SHEPHERD, EVENTS)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.RESET_TIMERS)
    ROBOT.reset()
    TINDER = LAST_TINDER
    BUTTONS = LAST_BUTTONS

    """
    CLIENTS = RuntimeClientManager()
    """
    disable_robots()

    lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.RESET)
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.RESET)
    print("RESET MATCH, MOVE TO SETUP")


def reset_state(args):
    """
    This is called after a match is complete because tinder and buttons are persisted across rounds for the same alliance but not when the next alliance begins.
    """
    global TINDER, BUTTONS
    TINDER = 0
    BUTTONS = Buttons()


def get_round(args):
    '''
    Retrieves all match info based on match number and sends this information to the UI. If not already cached, fetches info from the spreadsheet.
    '''
    # TODO: ADD EVERYTHING THAT SAM DESIRES, check the validation is good
    global MATCH_NUMBER, ROUND_NUMBER, ROBOT, TINDER, BUTTONS
    match_num = MATCH_NUMBER
    round_num = ROUND_NUMBER
    if "match_num" in args:
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
    Sends all match info to the UI
    '''
    global MATCH_NUMBER, ROUND_NUMBER, ROBOT, TINDER, BUTTONS
    team_num = ROBOT.number
    team_name = ROBOT.name
    lcm_data = {"match_num": MATCH_NUMBER, "round_num": ROUND_NUMBER,
                "team_num": team_num, "team_name": team_name, "custom_ip": ROBOT.custom_ip, "tinder": TINDER, "buttons": BUTTONS.illuminated}
    lcm_send(LCM_TARGETS.UI, UI_HEADER.TEAMS_INFO, lcm_data)


def set_custom_ip(args):
    ROBOT.custom_ip = args["custom_ip"]
    #TODO can robot be none? 
    #TODO send back connection status

def score_adjust(args):
    '''
    Allow for score to be changed based on referee decisions
    '''
    global STATE
    time, penalty, stamp_time = args.get("time"), args.get(
        "penalty"), args.get("stamp_time")
    if STATE == STATE.END or STATE == STATE.SETUP:
        ROBOT.elapsed_time = time if time is not None else ROBOT.elapsed_time
    ROBOT.penalty = penalty if penalty is not None else ROBOT.penalty
    ROBOT.stamp_time = stamp_time if stamp_time is not None else ROBOT.stamp_time
    # TODO: send dummy elapsed time if during game (-1) maybe this should be none
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORES, {
             "time": time, "penalty": penalty, "stamp_time": stamp_time, "score": ROBOT.total_time()})
    get_score({})

def get_score(args):
    '''
    Send the current score to the UI.
    '''
    ROBOT.calculate_time()
    lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES, {
        "time": ROBOT.elapsed_time,
        "penalty": ROBOT.penalty,
        "stamp_time": ROBOT.stamp_time,
        "score": ROBOT.total_time(),
        "start_time": ROBOT.start_time_millis()
    })


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
    try:
        # TODO: why si this "auto" and "telop" instead of 0/1?
        CLIENTS.send_mode(Mode.AUTO if autonomous else Mode.TELEOP)
    except Exception as exc:
        for client in CLIENTS.clients:
            try:
                client.set_mode(Mode.AUTO if autonomous else Mode.TELEOP)
            except Exception as exc:
                print("A robot failed to be enabled! Big sad :(")
                log(exc)


def disable_robots():
    '''
    Sends message to Dawn to disable all robots
    '''
    try:
        CLIENTS.send_mode(Mode.IDLE)
    except Exception as exc:
        for client in CLIENTS.clients:
            try:
                client.set_mode(Mode.IDLE)
            except Exception as exc:
                print("a client has disconnected")
        log(exc)
        print(exc)

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
    Send message to Dawn to disable the robots of team
    '''
    try:
        team_number = args["team_number"]
        client = CLIENTS.clients[int(team_number)]
        if client:
            client.set_mode("idle")
    except Exception as exc:
        log(exc)


def final_score(args):
    '''
    send shepherd the final score, send score to scoreboard
    '''
    ROBOT.calculate_time()
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORES, {
             "time": ROBOT.elapsed_time, "penalty": ROBOT.penalty, "stamp_time": ROBOT.stamp_time, "score": ROBOT.total_time()})


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

def check_code(args):
    '''
    Check the coding challenges and act appropriately
    '''
    ROBOT.coding_challenge = get_results(ROBOT.custom_ip)

# ----------
# AUTO STAGE
# ----------


def to_city(args):
    '''
    Go to the city stage
    '''
    global GAME_STATE
    enable_robots(False)
    GAME_TIMER.reset()
    GAME_TIMER.start_timer(CONSTANTS.TELEOP_TIME)
    if STOPLIGHT_TIMER.is_running():
        stoplight_penalty()
    GAME_STATE = STATE.CITY
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE, "start_time": str(ROBOT.start_time)})
    lcm_send(LCM_TARGETS.UI, UI_HEADER.STAGE, {
             "stage": GAME_STATE, "start_time": str(ROBOT.start_time)})
    print("ENTERING CITY STATE")

# ----------
# CITY STAGE
# ----------


def stoplight_timer_end(args):
    # turn stoplight green
    STOPLIGHT_TIMER.reset()


def stoplight_button_press(args):
    '''
    Triggered by a press of the stoplight button
    '''
    if ROBOT.pass_coding_challenges(n=4, tier=1):
        stoplight_timer_end([])


def stoplight_penalty():
    # whatever the penalty is
    pass


def to_forest(args):
    '''
    Go to the forest stage
    '''
    global GAME_STATE
    GAME_STATE = STATE.FOREST

def drawbridge_shortcut(args):
    pass
    #TODO activate the drawbridge

# ----------
# FOREST STAGE
# ----------


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
    if ROBOT.pass_coding_challenges(n=1, tier=1) == 0:
        SANDSTORM_TIMER.start_timer(CONSTANTS.SANDSTORM_COVER_TIME)
        # TODO: obscure vision

# ----------
# SANDSTORM STAGE
# ----------


def sandstorm_timer_end(args):
    # TODO: un-obscure vision
    pass


def to_dehydration(args):
    '''
    Go to the dehydration stage
    '''
    global GAME_STATE
    GAME_STATE = STATE.DEHYDRATION
    DEHYDRATION_TIMER.start_timer(CONSTANTS.DEHYRATION_TIME)
    # TODO: distribution of which challenges are chosen for each button?
    BUTTONS.illuminate_buttons(ROBOT)

# ----------
# DEHYDRATION STAGE
# ----------


def dehydration_button_press(args):
    '''
    Triggered when dehydration button is pressed
    '''
    global GAME_STATE
    button_number = int(args["button"])
    if BUTTONS.press_button_and_check(button_number):
        DEHYDRATION_TIMER.reset()  # stop dehydration timer so it doesn't run out
        GAME_STATE = STATE.FIRE


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


def toggle_fire(args):
    '''
    Toggle the fire.
    '''
    global FIRE_LIT
    if not FIRE_LIT:
        # TODO: light fire on field
        FIRE_LIT = True
    else:
        FIRE_LIT = False


def to_hypothermia(args):
    '''
    Go to the hypothermia zone in the forest biome.
    '''
    global GAME_STATE, FIRE_LIT
    GAME_STATE = STATE.HYPOTHERMIA
    if not FIRE_LIT:
        CLIENTS.send_game_state(State.HYPOTHERMIA_START)

# ----------
# HYPOTHERMIA STAGE
# ----------


def to_final(args):
    '''
    Go to the airport stage.
    '''
    global GAME_STATE
    GAME_STATE = STATE.FINAL
    CLIENTS.send_game_state(State.HYPOTHERMIA_STOP)

# ----------
# AIRPORT STAGE
# ----------


def to_end(args):
    '''
    Go to the end state.
    '''
    global GAME_STATE, LAST_TINDER, LAST_BUTTONS
    LAST_TINDER = TINDER
    LAST_BUTTONS = BUTTONS
    GAME_STATE = STATE.END
    disable_robots()
    ROBOT.end_time = time.time()
    ROBOT.calculate_time()
    lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
             {"time": ROBOT.elapsed_time, "penalty": ROBOT.penalty})
    GAME_STATE = STATE.END
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.SCORES, {"time": ROBOT.elapsed_time, "penalty": ROBOT.penalty, "stamp_time": ROBOT.stamp_time, "score": ROBOT.total_time()})
    lcm_send(LCM_TARGETS.SCOREBOARD,
             SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    lcm_send(LCM_TARGETS.UI, UI_HEADER.STAGE, {"stage": GAME_STATE})


###########################################
# Event to Function Mappings for each Stage
###########################################
SETUP_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_auto,
    SHEPHERD_HEADER.CODE_RETRIEVAL: check_code,
    SHEPHERD_HEADER.SET_GAME_INFO: set_game_info,
    SHEPHERD_HEADER.SET_CUSTOM_IP: set_custom_ip,
    SHEPHERD_HEADER.RESET_MATCH: reset_state
}

AUTO_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STOPLIGHT_TIMER_END: stoplight_timer_end,
    SHEPHERD_HEADER.AUTO_TRACK_COMPLETE: to_city,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_city
}

CITY_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.STOPLIGHT_TIMER_END: stoplight_timer_end,
    SHEPHERD_HEADER.STOPLIGHT_BUTTON_PRESS: stoplight_button_press,
    SHEPHERD_HEADER.STOPLIGHT_PENALTY: stoplight_penalty,
    SHEPHERD_HEADER.DRAWBRIDGE_SHORTCUT: drawbridge_shortcut,
    SHEPHERD_HEADER.FOREST_ENTRY: to_forest
}

FOREST_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.CONTACT_WALL: contact_wall,
    SHEPHERD_HEADER.DRAWBRIDGE_SHORTCUT: drawbridge_shortcut,
    SHEPHERD_HEADER.DESERT_ENTRY: to_desert
}

SANDSTORM_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.DEHYDRATION_ENTRY: to_dehydration,
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
    SHEPHERD_HEADER.TOGGLE_FIRE: toggle_fire,
    SHEPHERD_HEADER.HYPOTHERMIA_ENTRY: to_hypothermia,
    SHEPHERD_HEADER.SANDSTORM_TIMER_END: sandstorm_timer_end
}

HYPOTHERMIA_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.FINAL_ENTRY: to_final
}

FINAL_FUNCTIONS = {
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.CROSS_FINISH_LINE: to_end
}

END_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.GET_ROUND_INFO: get_round,
    SHEPHERD_HEADER.FINAL_SCORE: final_score,
    SHEPHERD_HEADER.SET_GAME_INFO: set_game_info,
    SHEPHERD_HEADER.RESET_MATCH: reset_state
}

EVERYWHERE_FUNCTIONS = {
    SHEPHERD_HEADER.GET_ROUND_INFO_NO_ARGS: send_round_info,
    SHEPHERD_HEADER.GET_SCORES: get_score,
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
