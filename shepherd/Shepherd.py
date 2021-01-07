import argparse
import queue
import random
import time
import datetime
import traceback
from datetime import datetime
from Alliance import *
from LCM import *
from Timer import *
from Utils import *
from Code import *
# TODO: import protos and change things like "auto" to Mode.AUTO
from runtimeclient import RuntimeClientManager
import Sheet
import bot
import audio
from Robot import Robot
import Field


clients = RuntimeClientManager((), ())

__version__ = (1, 0, 0)


###########################################
# Evergreen Methods
###########################################

#pylint: disable=broad-except
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
        if GAME_STATE == STATE.SETUP:
            func = SETUP_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Setup")
        elif GAME_STATE == STATE.AUTO:
            func = AUTO_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Auto")
        elif GAME_STATE == STATE.CITY:
            func = CITY_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in City")
        elif GAME_STATE == STATE.FOREST:
            func = FOREST_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Forest")
        elif GAME_STATE == STATE.SANDSTORM:
            func = SANDSTORM_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Sandstorm")
        elif GAME_STATE == STATE.DEHYDRATION:
            func = DEHYDRATION_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Dehydration")
        elif GAME_STATE == STATE.FIRE:
            func = FIRE_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Fire")
        elif GAME_STATE == STATE.HYPOTHERMIA:
            func = HYPOTHERMIA_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Hypothermia")
        elif GAME_STATE == STATE.FINAL:
            func = FINAL_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in Final")
        elif GAME_STATE == STATE.END:
            func = END_FUNCTIONS.get(payload[0])
            if func is not None:
                func(payload[1])
            else:
                print("Invalid Event in End")

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

    reset()

    #code_setup()

    name, num, alliance = args["name"], args["num"], args["alliance"]
    custom_ip = args["custom_ip"] or None

    ROBOT = Robot(name, num, alliance, custom_ip)

    # LCM send to scoreboard about robot

    GAME_STATE = STATE.SETUP
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    print("ENTERING SETUP STATE")

def to_auto(args):
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    #pylint: disable= no-member
    global GAME_STATE, ROBOT
    global clients
    try:
        clients = RuntimeClientManager()
        clients.get_clients([ROBOT.custom_ip])
    except Exception as exc:
        log(exc)
        return
    GAME_TIMER.start_timer(CONSTANTS.AUTO_TIME + 2)
    #The +2 is a lag compensation and honestly we should work on removing it.
    GAME_STATE = STATE.AUTO
    ROBOT.start_time = datetime.now()
    STOPLIGHT_TIMER.start_timer(CONSTANTS.STOPLIGHT_TIME)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    enable_robots(True)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE_TIMER_START,
             {"time" : CONSTANTS.AUTO_TIME})
    print("ENTERING AUTO STATE")

def to_end(args):
    '''
    Move to end stage after the match ends. Robots should be disabled here
    and final score adjustments can be made.
    '''
    global GAME_STATE
    lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
             {"blue_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.BLUE].score),
              "gold_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.GOLD].score)})
    GAME_STATE = STATE.END
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})
    disable_robots()
    print("ENTERING END STATE")

def reset(args=None):
    # TODO: this should be reset round i.e. go to the tinder and buttons pressed of the previous round.
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global GAME_STATE, EVENTS, clients, ROBOT
    GAME_STATE = STATE.SETUP
    Timer.reset_all()
    EVENTS = queue.Queue()
    lcm_start_read(LCM_TARGETS.SHEPHERD, EVENTS)
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.RESET_TIMERS)
    ROBOT.reset()

    send_connections(None) # currently does nothing
    clients = RuntimeClientManager()
    disable_robots()

    lcm_send(LCM_TARGETS.TABLET, TABLET_HEADER.RESET)
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.RESET)
    print("RESET MATCH, MOVE TO SETUP")

def get_match(args):
    '''
    Retrieves the match based on match number and sends this information to the UI
    '''
    match_num = int(args["match_num"])
    info = Sheet.get_match(match_num)
    info["match_num"] = match_num
    lcm_send(LCM_TARGETS.UI, UI_HEADER.TEAMS_INFO, info)

def score_adjust(args):
    '''
    Allow for score to be changed based on referee decisions
    '''
    time, penalty = args["time"], args["penalty"]
    ROBOT.elapsed_time = time
    ROBOT.penalty = penalty

    # TODO: update lcm send
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE,
             {"alliance" : ALLIANCES[ALLIANCE_COLOR.BLUE].name,
              "score" : math.floor(ALLIANCES[ALLIANCE_COLOR.BLUE].score)})

def get_score(args):
    '''
    Send the current blue and gold score to the UI
    '''
    # TODO: update lcm send
    if ALLIANCES[ALLIANCE_COLOR.BLUE] is None:
        lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
                 {"blue_score" : None,
                  "gold_score" : None})
    else:
        lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
                 {"blue_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.BLUE].score),
                  "gold_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.GOLD].score)})

def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    if ALLIANCES[ALLIANCE_COLOR.BLUE] is not None:
        Sheet.write_scores(MATCH_NUMBER, ALLIANCES[ALLIANCE_COLOR.BLUE].score,
                           ALLIANCES[ALLIANCE_COLOR.GOLD].score)
    return -1

def enable_robots(autonomous):
    '''
    Sends message to Runtime to enable all robots. The argument should be a boolean
    which is true if we are entering autonomous mode
    '''
    try:
        clients.set_mode("auto" if autonomous else "teleop")
    except Exception as exc:
        for client in clients.clients:
            try:
                client.set_mode("auto" if autonomous else "teleop")
            except Exception as exc:
                print("A robot failed to be enabled! Big sad :(")
                log(exc)

def disable_robots():
    '''
    Sends message to Dawn to disable all robots
    '''
    try:
        clients.set_mode("idle")
    except Exception as exc:
        for client in clients.clients:
            try:
                client.set_mode("idle")
            except Exception as exc:
                print("a client has disconnected")
        log(exc)
        print(exc)

#pylint: disable=redefined-builtin
def log(Exception):
    global LAST_HEADER
    # if Shepherd.MATCH_NUMBER <= 0:
    #     return
    now = datetime.datetime.now()
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
        client = clients.clients[int(team_number)]
        if client:
            client.set_mode("idle")
    except Exception as exc:
        log(exc)


def set_master_robot(args):
    '''
    Set the master robot of the alliance
    '''
    alliance = args["alliance"]
    team_number = args["team_num"]
    MASTER_ROBOTS[alliance] = team_number
    msg = {"alliance": alliance, "team_number": int(team_number)}
    lcm_send(LCM_TARGETS.DAWN, DAWN_HEADER.MASTER, msg)

def final_score(args):
    '''
    send shepherd the final score, send score to scoreboard
    '''
    blue_final = args['blue_score']
    gold_final = args['gold_score']
    ALLIANCES[ALLIANCE_COLOR.GOLD].score = gold_final
    ALLIANCES[ALLIANCE_COLOR.BLUE].score = blue_final
    msg = {"alliance": ALLIANCE_COLOR.GOLD, "amount": gold_final}
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE, msg)
    msg = {"alliance": ALLIANCE_COLOR.BLUE, "amount": blue_final}
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.SCORE, msg)

def set_connections(args):
    """Set connections"""
    #pylint: disable=undefined-variable, not-an-iterable
    team = args["team_number"]
    connection = boolean(args["connection"])
    dirty = False
    for alliance in ALLIANCES.values:
        if team == alliance.team_1_number:
            if alliance.team_1_connection != connection:
                alliance.team_1_connection = connection
                dirty = True
        if team == alliance.team_2_number:
            if alliance.team_2_connection != connection:
                alliance.team_2_connection = connection
                dirty = True
    if dirty:
        send_connections(None)

def send_connections(args):
    """Send connections"""
    pass #pylint: disable=unnecessary-pass
    # msg = {"g_1_connection" : ALLIANCES[ALLIANCE_COLOR.GOLD].team_1_connection,
    #        "g_2_connection" : ALLIANCES[ALLIANCE_COLOR.GOLD].team_2_connection,
    #        "b_1_connection" : ALLIANCES[ALLIANCE_COLOR.BLUE].team_1_connection,
    #        "b_2_connection" : ALLIANCES[ALLIANCE_COLOR.BLUE].team_2_connection}
    # lcm_send(LCM_TARGETS.UI, UI_HEADER.CONNECTIONS, msg)

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

# ----------
# AUTO STAGE
# ----------

# TODO: traffic sig_

def to_city(args):
    '''
    Go to the city stage
    '''
    global GAME_STATE
    enable_robots(False)
    GAME_TIMER.reset()
    GAME_TIMER.start_timer(CONSTANTS.TELEOP_TIME)
    # TODO: stopwatch for course time
    if STOPLIGHT_TIMER.is_running():
        stoplight_penalty()
    GAME_STATE = STATE.CITY

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
    if ROBOT.pass_all_coding_challenges():
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

# ----------
# FOREST STAGE
# ----------

def contact_wall(args):
    '''
    Triggered when the robot hits the wall
    '''
    lcm_send(LCM_TARGETS.RUNTIME, RUNTIME_HEADER.REVERSE_TEN_SECONDS, {})

def to_desert(args):
    '''
    Go to the sandstorm stage
    '''
    global GAME_STATE
    GAME_STATE = STATE.SANDSTORM
    if ROBOT.pass_coding_challenges(n=1) == 0:
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
    FIELD.illuminate_buttons(ROBOT)

# ----------
# DEHYDRATION STAGE
# ----------

def dehydration_button_press(args):
    '''
    Triggered when dehydration button is pressed
    '''
    global GAME_STATE
    button_number = int(args["button"])
    if FIELD.press_button_and_check(button_number):
        DEHYDRATION_TIMER.reset() # stop dehydration timer so it doesn't run out
        GAME_STATE = STATE.FIRE


def dehydration_penalty_timer_start(args):
    '''
    Triggered when robot gets dehydrated ("water getting" timer runs out). Starts the penalty timer and forcibly stops the robot.
    '''
    ROBOT_DEHYDRATED_TIMER.start_timer(CONSTANTS.ROBOT_DEHYDRATED_TIME)
    lcm_send(LCM_TARGETS.RUNTIME, RUNTIME_HEADER.STOP_ROBOT, {})

def dehydration_penalty_timer_end(args):
    '''
    Triggered when robot dehydration ends.
    '''
    global GAME_STATE
    GAME_STATE = STATE.FIRE
    lcm_send(LCM_TARGETS.RUNTIME, RUNTIME_HEADER.START_ROBOT, {})


# ----------
# FIRE STAGE
# ----------

def collect_tinder(args):
    '''
    This method collects one more tinder
    1 tinder = fire is lit for one round.
    2 tinder = fire is lit for two rounds.
    3 tinder = fire is lit for three rounds.
    '''
    global TINDER
    TINDER += 1

def toggle_fire(args):
    '''
    Toggle the fire.
    '''
    global FIRE_LIT
    if not FIRE_LIT:
        # TODO: light fire
        FIRE_LIT = True
    else:
        FIRE_LIT = False

def to_hypothermia(args):
    '''
    Go to the hypothermia zone in the forest biome.
    '''
    global GAME_STATE
    GAME_STATE = STATE.HYPOTHERMIA

# ----------
# HYPOTHERMIA STAGE
# ----------

def to_final(args):
    '''
    Go to the airport stage.
    '''
    global GAME_STATE
    GAME_STATE = STATE.AIRPORT

# ----------
# AIRPORT STAGE
# ----------

def to_end(args):
    '''
    Go to the end state.
    '''
    global GAME_STATE
    GAME_STATE = STATE.END
    disable_robots()
    ROBOT.end_time = datetime.now()
    # TODO: update scoreboard header and pass time instead of score
    lcm_send(LCM_TARGETS.UI, UI_HEADER.SCORES,
            {"blue_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.BLUE].score),
            "gold_score" : math.floor(ALLIANCES[ALLIANCE_COLOR.GOLD].score)})
    GAME_STATE = STATE.END
    lcm_send(LCM_TARGETS.SCOREBOARD, SCOREBOARD_HEADER.STAGE, {"stage": GAME_STATE})


###########################################
# Event to Function Mappings for each Stage
###########################################

SETUP_FUNCTIONS = {
    SHEPHERD_HEADER.SETUP_MATCH: to_setup,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.GET_MATCH_INFO : get_match,
    SHEPHERD_HEADER.START_NEXT_STAGE: to_auto,
    SHEPHERD_HEADER.CODE_RETRIEVAL: check_code
}

AUTO_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STOPLIGHT_TIMER_END: stoplight_timer_end,
    SHEPHERD_HEADER.AUTO_TRACK_COMPLETE: to_city,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_city
}

CITY_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.AUTO_TRACK_COMPLETE: to_city,
    SHEPHERD_HEADER.STOPLIGHT_TIMER_END: stoplight_timer_end,
    SHEPHERD_HEADER.STOPLIGHT_BUTTON_PRESS: stoplight_button_press,
    SHEPHERD_HEADER.STOPLIGHT_PENALTY: stoplight_penalty,
    SHEPHERD_HEADER.FOREST_ENTRY: to_forest
}

FOREST_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.CONTACT_WALL: contact_wall,
    SHEPHERD_HEADER.DESERT_ENTRY: to_desert
}

SANDSTORM_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.DEHYDRATION_ENTRY: to_dehydration,
    SHEPHERD_HEADER.SANDSTORM_TIMER_END: sandstorm_timer_end
}

DEHYDRATION_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.DEHYDRATION_BUTTON_PRESS: dehydration_button_press,
    SHEPHERD_HEADER.DEHYDRATION_TIMER_END: dehydration_penalty_timer_start,
    SHEPHERD_HEADER.ROBOT_DEHYDRATED_TIMER_END: dehydration_penalty_timer_end,
    SHEPHERD_HEADER.SANDSTORM_TIMER_END: sandstorm_timer_end
}

FIRE_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.COLLECT_TINDER: collect_tinder,
    SHEPHERD_HEADER.TOGGLE_FIRE: toggle_fire,
    SHEPHERD_HEADER.HYPOTHERMIA_ENTRY: to_hypothermia,
    SHEPHERD_HEADER.SANDSTORM_TIMER_END: sandstorm_timer_end
}

HYPOTHERMIA_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.FINAL_ENTRY: to_final
}

AIRPORT_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.ROBOT_OFF : disable_robot,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections,
    SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
    SHEPHERD_HEADER.CROSS_FINISH_LINE: to_end
}

END_FUNCTIONS = {
    SHEPHERD_HEADER.RESET_ROUND : reset,
    SHEPHERD_HEADER.SCORE_ADJUST : score_adjust,
    SHEPHERD_HEADER.GET_SCORES : get_score,
    SHEPHERD_HEADER.SETUP_MATCH : to_setup,
    SHEPHERD_HEADER.GET_MATCH_INFO : get_match,
    SHEPHERD_HEADER.FINAL_SCORE : final_score,
    SHEPHERD_HEADER.ROBOT_CONNECTION_STATUS: set_connections,
    SHEPHERD_HEADER.REQUEST_CONNECTIONS: send_connections
}

###########################################
# Evergreen Variables
###########################################

GAME_STATE = STATE.END
GAME_TIMER = Timer(TIMER_TYPES.MATCH)
STOPLIGHT_TIMER = Timer(TIMER_TYPES.STOPLIGHT_WAIT)
SANDSTORM_TIMER = Timer(TIMER_TYPES.SANDSTORM_COVER)
DEHYDRATION_TIMER = Timer(TIMER_TYPES.DEHYDRATION)
ROBOT_DEHYDRATED_TIMER = Timer(TIMER_TYPES.ROBOT_DEHYDRATED)
ROBOT = None
FIELD = None

MATCH_NUMBER = -1
ALLIANCES = {ALLIANCE_COLOR.GOLD: None, ALLIANCE_COLOR.BLUE: None}
EVENTS = None

LAST_HEADER = None

###########################################
# Game Specific Variables
###########################################
BUTTONS = {'gold_1': False, 'gold_2': False, 'blue_1': False, 'blue_2': False}
STARTING_SPOTS = ["unknown", "unknown", "unknown", "unknown"]
MASTER_ROBOTS = {ALLIANCE_COLOR.BLUE: None, ALLIANCE_COLOR.GOLD: None}

STUDENT_DECODE_TIMER = Timer(TIMER_TYPES.STUDENT_DECODE)

CODES_USED = []

###########################################
# 2020 Game Specific Variables
###########################################
TINDER = 0
FIRE_LIT = False

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
