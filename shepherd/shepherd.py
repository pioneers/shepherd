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
from runtimeclient import RuntimeClientManager
from protos.run_mode_pb2 import Mode
from protos.game_state_pb2 import State
from sheet import Sheet
from robot import Robot
from challenge_results import CHALLENGE_RESULTS



###########################################
# Evergreen Variables
###########################################

MATCH_NUMBER = -1
GAME_STATE: str = STATE.END
GAME_TIMER = Timer(TIMER_TYPES.MATCH)

ALLIANCES = {
    ALLIANCE_COLOR.GOLD: Alliance(Robot("", -1), Robot("", -1)),
    ALLIANCE_COLOR.BLUE: Alliance(Robot("", -1), Robot("", -1)),
}

CLIENTS = RuntimeClientManager()


###########################################
# Game Specific Variables
###########################################


###########################################
# 2020 Game Specific Variables
###########################################


###########################################
# Evergreen Methods
###########################################




def start():
    '''
    Main loop which processes the event queue and calls the appropriate function
    based on game state and the dictionary of available functions
    '''
    events = queue.Queue()
    ydl_start_read(YDL_TARGETS.SHEPHERD, events)
    while True:
        print("GAME STATE OUTSIDE: ", GAME_STATE)
        payload = events.get(True)
        print(payload)

        if GAME_STATE in FUNCTION_MAPPINGS:
            func_list = FUNCTION_MAPPINGS.get(GAME_STATE)
            func = func_list.get(payload[0]) or EVERYWHERE_FUNCTIONS.get(payload[0])
            if func is not None:
                func(**payload[1]) #deconstructs dictionary into arguments
            else:
                print(f"Invalid Event in {GAME_STATE}")
        else:
            print(f"Invalid State: {GAME_STATE}")






def set_match_number(match_num):
    '''
    Retrieves all match info based on match number and sends this information to the UI. 
    If not already cached, fetches info from the spreadsheet, and caches it.
    '''
    global MATCH_NUMBER
    # if robot info is for the correct match
    if MATCH_NUMBER != match_num:
        MATCH_NUMBER = match_num
        info = Sheet.get_round(match_num)
        ALLIANCES[ALLIANCE_COLOR.BLUE] = Alliance(
            Robot(info["blue_1_name"], info["blue_1_num"]),
            Robot(info["blue_2_name"], info["blue_2_num"]))
        ALLIANCES[ALLIANCE_COLOR.GOLD] = Alliance(
            Robot(info["gold_1_name"], info["gold_1_num"]),
            Robot(info["gold_2_name"], info["gold_2_num"]))
        CLIENTS.connect_client(INDICES.BLUE_1, info("blue_1_ip"))
        CLIENTS.connect_client(INDICES.BLUE_2, info("blue_2_ip"))
        CLIENTS.connect_client(INDICES.GOLD_1, info("gold_1_ip"))
        CLIENTS.connect_client(INDICES.GOLD_2, info("gold_2_ip"))
    send_match_info_to_ui()


def to_setup(match_num, teams):
    '''
    loads the match information for the upcoming match, then
    calls reset_match() to move to setup state.
    By the end, should be ready to start match.
    '''
    global MATCH_NUMBER
    MATCH_NUMBER = match_num

    ALLIANCES[ALLIANCE_COLOR.BLUE].robot1.set_from_dict(teams[INDICES.BLUE_1])
    ALLIANCES[ALLIANCE_COLOR.BLUE].robot2.set_from_dict(teams[INDICES.BLUE_2])
    ALLIANCES[ALLIANCE_COLOR.GOLD].robot1.set_from_dict(teams[INDICES.GOLD_1])
    ALLIANCES[ALLIANCE_COLOR.GOLD].robot2.set_from_dict(teams[INDICES.GOLD_2])
    for i in range(4):
        CLIENTS.connect_client(i, teams[i]["robot_ip"])

    # so if there are other UIs open they get the update
    send_match_info_to_ui()
    # note that reset_match is what actually moves Shepherd into the setup state
    reset_match()


def reset_match():
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global GAME_STATE
    GAME_STATE = STATE.SETUP
    Timer.reset_all()
    disable_robots()
    CLIENTS.reset()
    CLIENTS.connect_all()
    ALLIANCES[ALLIANCE_COLOR.BLUE].reset()
    ALLIANCES[ALLIANCE_COLOR.GOLD].reset()
    send_state_to_ui()
    print("ENTERING SETUP STATE")


def to_auto():
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    global GAME_STATE
    GAME_STATE = STATE.AUTO
    GAME_TIMER.start_timer(CONSTANTS.AUTO_TIME)
    enable_robots(autonomous=True)
    send_state_to_ui()
    print("ENTERING AUTO STATE")


def to_teleop():
    global GAME_STATE
    GAME_STATE = STATE.TELEOP
    GAME_TIMER.start_timer(CONSTANTS.TELEOP_TIME)
    enable_robots(autonomous=False)
    send_state_to_ui()
    print("ENTERING TELEOP STATE")


def to_end():
    '''
    Go to the end state, finishing the game and flushing scores to the spreadsheet.
    '''
    global GAME_STATE
    GAME_STATE = STATE.END
    disable_robots()
    CLIENTS.reset()
    GAME_TIMER.reset()
    send_state_to_ui()
    send_score_to_ui()
    flush_scores()
    print("ENTERING END STATE")


def go_to_state(state):
    transitions = {
        STATE.SETUP: reset_match,
        STATE.AUTO: to_auto,
        STATE.TELEOP: to_teleop,
        STATE.END: to_end
    }
    if state in transitions:
        transitions[state]()
    else:
        print(f"Sorry, {state} is not a valid state to move to.")




def set_robot_ip(ind, ip):
    '''
    Sets the given client ip, and attempts to connect to it
    '''
    CLIENTS.connect_client(ind, ip)

def score_adjust(blue_score, gold_score):
    '''
    Allow for score to be changed based on referee decisions
    '''
    ALLIANCES[ALLIANCE_COLOR.BLUE].set_score(blue_score)
    ALLIANCES[ALLIANCE_COLOR.GOLD].set_score(gold_score)
    send_score_to_ui()
    flush_scores()



def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    Sheet.write_scores(
        MATCH_NUMBER,
        ALLIANCES[ALLIANCE_COLOR.BLUE].score,
        ALLIANCES[ALLIANCE_COLOR.GOLD].score
    )


def send_match_info_to_ui():
    '''
    Sends all match info to the UI
    '''
    ydl_data = {"match_num": MATCH_NUMBER, "teams": [
        ALLIANCES[ALLIANCE_COLOR.BLUE].robot1.info_dict(CLIENTS.clients[INDICES.BLUE_1].robot_url),
        ALLIANCES[ALLIANCE_COLOR.BLUE].robot2.info_dict(CLIENTS.clients[INDICES.BLUE_2].robot_url),
        ALLIANCES[ALLIANCE_COLOR.GOLD].robot1.info_dict(CLIENTS.clients[INDICES.GOLD_1].robot_url),
        ALLIANCES[ALLIANCE_COLOR.GOLD].robot2.info_dict(CLIENTS.clients[INDICES.GOLD_2].robot_url),
    ]}
    ydl_send(YDL_TARGETS.UI, UI_HEADER.TEAMS_INFO, ydl_data)

def send_score_to_ui():
    '''
    Sends the current score to the UI
    '''
    data = {
        "blue_score": ALLIANCES[ALLIANCE_COLOR.BLUE].score,
        "gold_score": ALLIANCES[ALLIANCE_COLOR.GOLD].score,
    }
    ydl_send(YDL_TARGETS.UI, UI_HEADER.SCORES, data)

def send_state_to_ui():
    '''
    Sends the GAME_STATE to the UI
    '''
    ydl_send(YDL_TARGETS.UI, UI_HEADER.STATE, {"state": GAME_STATE})

def send_connection_status_to_ui():
    '''
    Sends the connection status of all runtime clients to the UI
    '''
    CLIENTS.send_connection_status_to_ui()




###########################################
# Game Specific Methods
###########################################


def enable_robots(autonomous):
    '''
    Sends message to Runtime to enable all robots. The argument should be a boolean
    which is true if we are entering autonomous mode
    '''
    CLIENTS.send_mode(Mode.AUTO if autonomous else Mode.TELEOP)

def disable_robots():
    '''
    Sends message to Runtime to disable all robots
    '''
    CLIENTS.send_mode(Mode.IDLE)

def disable_robot(ind):
    '''
    Send message to Runtime to disable the robot of team
    '''
    CLIENTS.clients[ind].send_mode(Mode.IDLE)

def enable_robot(ind):
    '''
    Send message to Runtime to enable the robot of team
    '''
    mode = Mode.AUTO if GAME_STATE == STATE.AUTO else Mode.TELEOP
    CLIENTS.clients[ind].send_mode(mode)






###########################################
# Spring 2022 Game
###########################################






###########################################
# Event to Function Mappings for each Stage
###########################################

FUNCTION_MAPPINGS = {
    STATE.SETUP: {
        SHEPHERD_HEADER.SET_MATCH_NUMBER: set_match_number,
        SHEPHERD_HEADER.SETUP_MATCH: to_setup,
        SHEPHERD_HEADER.START_NEXT_STAGE: to_auto,
    },
    STATE.AUTO: {
        SHEPHERD_HEADER.STAGE_TIMER_END: to_teleop,
        SHEPHERD_HEADER.RESET_CURRENT_STAGE: to_auto,
        SHEPHERD_HEADER.START_NEXT_STAGE: to_teleop,
    },
    STATE.TELEOP: {
        SHEPHERD_HEADER.STAGE_TIMER_END: to_end,
        SHEPHERD_HEADER.RESET_CURRENT_STAGE: to_teleop,
        SHEPHERD_HEADER.START_NEXT_STAGE: to_end,
    },
    STATE.END: {
        SHEPHERD_HEADER.SET_MATCH_NUMBER: set_match_number,
        SHEPHERD_HEADER.SETUP_MATCH: to_setup,
        SHEPHERD_HEADER.SET_SCORES: score_adjust,
    }
}

EVERYWHERE_FUNCTIONS = {
    SHEPHERD_HEADER.GET_MATCH_INFO: send_match_info_to_ui,
    SHEPHERD_HEADER.GET_SCORES: send_score_to_ui,
    SHEPHERD_HEADER.GET_STATE: send_state_to_ui,
    SHEPHERD_HEADER.GET_CONNECTION_STATUS: send_connection_status_to_ui,

    SHEPHERD_HEADER.SET_STATE: go_to_state,
    SHEPHERD_HEADER.ROBOT_OFF: disable_robot,
    SHEPHERD_HEADER.ROBOT_ON: enable_robot,
    SHEPHERD_HEADER.SET_ROBOT_IP: set_robot_ip,
    SHEPHERD_HEADER.RESET_MATCH: reset_match,
}

if __name__ == '__main__':
    start()