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



###########################################
# Evergreen Variables
###########################################

MATCH_NUMBER = -1
GAME_STATE: str = STATE.END
GAME_TIMER = Timer(TIMER_TYPES.MATCH)

ALLIANCES = {ALLIANCE_COLOR.GOLD: Alliance(Robot(), Robot()), 
             ALLIANCE_COLOR.BLUE: Alliance(Robot(), Robot())}

CLIENTS = RuntimeClientManager() # TODO: ask Akshit whether to kill this


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
        # time.sleep(0.1) # TODO: remove this sleep?
        payload = events.get(True)
        LAST_HEADER = payload
        print(payload)

        if GAME_STATE in FUNCTION_MAPPINGS:
            func_list = funcmappings.get(GAME_STATE)
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

    # if robot info is for the correct match, round
    if MATCH_NUMBER != match_num:
        MATCH_NUMBER = match_num
        try:
            info = Sheet.get_round(match_num, round_num)
            ALLIANCES[ALLIANCE_COLOR.BLUE] = Alliance(Robot(), Robot()) # TODO: how does this work
            ALLIANCES[ALLIANCE_COLOR.GOLD] = Alliance(Robot(), Robot()) # TODO: how does this work
        except Exception as e:
            print("Exception while reading from sheet:",e)
    send_match_info_to_ui()


def to_setup(match_num, b1, b2, g1, g2):
    '''
    loads the match information for the upcoming match, then
    calls reset_match() to move to setup state.
    By the end, should be ready to start match.
    '''
    global MATCH_NUMBER
    MATCH_NUMBER = match_num
    ALLIANCES[ALLIANCE_COLOR.BLUE] = Alliance(Robot(), Robot()) # TODO: how does this work
    ALLIANCES[ALLIANCE_COLOR.GOLD] = Alliance(Robot(), Robot()) # TODO: how does this work

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
    connect()
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
    #pylint: disable= no-member
    global GAME_STATE
    GAME_STATE = STATE.AUTO
    GAME_TIMER.start_timer(CONSTANTS.AUTO_TIME)
    enable_robots(True)
    send_state_to_ui()
    print("ENTERING AUTO STATE")


def to_teleop():
    global GAME_STATE
    GAME_STATE = STATE.TELEOP
    GAME_TIMER.start_timer(CONSTANTS.TELEOP_TIME)
    enable_robots(False)
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




def set_robot_ip(team_number, ip):
    # TODO: fill in
    pass

def connect():
    # TODO: fill in
    # CLIENTS.get_clients([ROBOT.custom_ip], [ROBOT])


def score_adjust(blue_score, gold_score):
    '''
    Allow for score to be changed based on referee decisions
    '''
    # TODO: fill in
    ALLIANCES[ALLIANCE_COLOR.BLUE].set_score(blue_score)
    ALLIANCES[ALLIANCE_COLOR.GOLD].set_score(gold_score)
    send_score_to_ui()
    flush_scores()



def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    try:
        Sheet.write_scores(MATCH_NUMBER, ROUND_NUMBER, ROBOT.total_time())
    except Exception as e:
        print(f"Unable to push scores to spreadsheet: {e}")


def send_match_info_to_ui():
    '''
    Sends all match info to the UI
    '''
    team_num = ROBOT.number
    team_name = ROBOT.name
    ydl_data = {"match_num": MATCH_NUMBER, "round_num": ROUND_NUMBER,
                "team_num": team_num, "team_name": team_name, "custom_ip": ROBOT.custom_ip, "tinder": TINDER, "buttons": BUTTONS.illuminated}
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
    CLIENTS.send_connection_status_to_ui() #TODO: runtimeclientmanager done? 
    
    
    

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

def disable_robot(args):
    '''
    Send message to Runtime to disable the robot of team
    '''
    disable_robots() #hotfix, no idea why other doesn't work
    #send_robot_mode(int(args["team_number"]), Mode.IDLE)

def enable_robot(args):
    '''
    Send message to Runtime to enable the robot of team
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
        print(msg)





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
