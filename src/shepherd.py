import threading
import time
from ydl import Client, Handler
from alliance import Alliance
from timer import TimerGroup, Timer
from utils import *
from runtimeclient import RuntimeClientManager
from protos.run_mode_pb2 import IDLE, AUTO, TELEOP
from protos.gamestate_pb2 import State
from sheet import Sheet
from robot import Robot


###########################################
# Evergreen Variables
###########################################
YC = Client(YDL_TARGETS.SHEPHERD)
MATCH_NUMBER: int = -1
GAME_STATE: str = STATE.END
TIMERS = TimerGroup()
GAME_TIMER = Timer(TIMERS,
                   lambda: YC.send(SHEPHERD_HEADER.STAGE_TIMER_END()))
# BLIZZARD_WARNING_TIMER = Timer(TIMERS,
#     lambda: YC.send(SHEPHERD_HEADER.SOUND_BLIZZARD_WARNING()))

ALLIANCES = {
    ALLIANCE_COLOR.GOLD: Alliance(Robot("", -1), Robot("", -1)),
    ALLIANCE_COLOR.BLUE: Alliance(Robot("", -1), Robot("", -1)),
}

CLIENTS = RuntimeClientManager(YC)


###########################################
# Game Specific Variables
###########################################
GOLD_CHEAT_CODE = None
BLUE_CHEAT_CODE = None

###########################################
# Evergreen Methods
###########################################


def start():
    '''
    Main loop which processes the event queue and calls the appropriate function
    based on game state and the dictionary of available functions
    '''
    while True:
        payload = YC.receive()
        print("GAME STATE OUTSIDE: ", GAME_STATE)
        print(payload)

        if GAME_STATE in STATE_HANDLERS:
            handler = STATE_HANDLERS.get(GAME_STATE)
            handler.handle(payload)
        else:
            print(f"Invalid State: {GAME_STATE}")


def pull_from_sheets():
    while True:
        # if GAME_STATE not in [STATE.SETUP]:
        if not TIMERS.is_paused() and GAME_STATE not in [STATE.END, STATE.SETUP]:
            Sheet.send_scores_for_icons(MATCH_NUMBER)
        time.sleep(2.0)


@SHEPHERD_HANDLER.SETUP.on(SHEPHERD_HEADER.SET_MATCH_NUMBER)
@SHEPHERD_HANDLER.END.on(SHEPHERD_HEADER.SET_MATCH_NUMBER)
def set_match_number(match_num):
    '''
    Retrieves all match info based on match number and sends this information to the UI.
    If not already cached, fetches info from the spreadsheet, and caches it.
    Fetching info from spreadsheet is asynchronous, will send a ydl header back with results
    '''
    global MATCH_NUMBER
    # if MATCH_NUMBER != match_num:
    #     MATCH_NUMBER = match_num
    #     Sheet.get_match(match_num)
    # else:
    #     send_match_info_to_ui()
    MATCH_NUMBER = match_num
    Sheet.get_match(match_num)


@SHEPHERD_HANDLER.SETUP.on(SHEPHERD_HEADER.SET_TEAMS_INFO)
@SHEPHERD_HANDLER.END.on(SHEPHERD_HEADER.SET_TEAMS_INFO)
def set_teams_info(teams):
    '''
    Caches info and sends it to any open UIs.
    '''
    ALLIANCES[ALLIANCE_COLOR.BLUE].robot1.set_from_dict(teams[INDICES.BLUE_1])
    ALLIANCES[ALLIANCE_COLOR.BLUE].robot2.set_from_dict(teams[INDICES.BLUE_2])
    ALLIANCES[ALLIANCE_COLOR.GOLD].robot1.set_from_dict(teams[INDICES.GOLD_1])
    ALLIANCES[ALLIANCE_COLOR.GOLD].robot2.set_from_dict(teams[INDICES.GOLD_2])
    for i in range(4):
        CLIENTS.connect_client(i, teams[i]["robot_ip"])
    # even if source of info is UI, needs to be forwarded to other open UIs
    send_match_info_to_ui()


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.PAUSE_TIMER)
def pause_timer():
    '''
    Pauses a running match. Invalid to call during setup and end.
    '''
    if not TIMERS.is_paused():
        TIMERS.pause()
        disable_robots()
        YC.send(UI_HEADER.PAUSE_TIMER())


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.RESUME_TIMER)
def resume_timer():
    '''
    Resumes a running match. Invalid to call during setup and end.
    '''
    if TIMERS.is_paused():
        TIMERS.resume()
        enable_robots(autonomous=(GAME_STATE == STATE.AUTO))
        end_time, _ = GAME_TIMER.status()
        YC.send(UI_HEADER.RESUME_TIMER(
            end_time=end_time, pause_end=time.time()))


###########################################
# Transition Methods
###########################################

@SHEPHERD_HANDLER.SETUP.on(SHEPHERD_HEADER.SETUP_MATCH)
@SHEPHERD_HANDLER.END.on(SHEPHERD_HEADER.SETUP_MATCH)
def to_setup(match_num, teams):
    '''
    loads the match information for the upcoming match, then
    calls reset_match() to move to setup state.
    By the end, should be ready to start match.
    '''
    if Sheet.write_match_info(match_num, teams) == False:
        return
    global MATCH_NUMBER
    MATCH_NUMBER = match_num
    set_teams_info(teams)
    # note that reset_match is what actually moves Shepherd into the setup state
    reset_match()


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.RESET_MATCH)
def reset_match():
    '''
    Resets the current match, moving back to the setup stage but with the current teams loaded in.
    Should reset all state being tracked by Shepherd.
    ****THIS METHOD MIGHT NEED UPDATING EVERY YEAR BUT SHOULD ALWAYS EXIST****
    '''
    global GAME_STATE
    GAME_STATE = STATE.SETUP
    TIMERS.reset_all()
    disable_robots()
    CLIENTS.reconnect_all()
    ALLIANCES[ALLIANCE_COLOR.BLUE].reset()
    ALLIANCES[ALLIANCE_COLOR.GOLD].reset()

    send_state_to_ui()
    print("ENTERING SETUP STATE")

    # temporary code for exhibition, remove later
    YC.send(UI_HEADER.SCORES(
        blue_score=ALLIANCES[ALLIANCE_COLOR.BLUE].score,
        gold_score=ALLIANCES[ALLIANCE_COLOR.GOLD].score
    ))


def set_state(state):
    global GAME_STATE
    GAME_STATE = state
    send_state_to_ui()
    print(f"ENTERING {state} STATE")


@SHEPHERD_HANDLER.SETUP.on(SHEPHERD_HEADER.START_NEXT_STAGE)
def to_auto():
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    GAME_TIMER.start(STAGE_TIMES[STATE.AUTO])
    enable_robots(autonomous=True)
    YC.send(UI_HEADER.PLAY_START_SOUND())
    set_state(STATE.AUTO)


@SHEPHERD_HANDLER.AUTO.on(SHEPHERD_HEADER.STAGE_TIMER_END)
def to_teleop():
    GAME_TIMER.start(STAGE_TIMES[STATE.TELEOP_1])
    # BLIZZARD_WARNING_TIMER.start(CONSTANTS.BLIZZARD_WARNING_TIME)
    enable_robots(autonomous=False)
    set_state(STATE.TELEOP_1)


@SHEPHERD_HANDLER.TELEOP_1.on(SHEPHERD_HEADER.STAGE_TIMER_END)
def to_end():
    '''
    Go to the end state, finishing the game and flushing scores to the spreadsheet.
    '''
    global GAME_STATE
    GAME_STATE = STATE.END
    disable_robots()
    YC.send(UI_HEADER.PLAY_END_SOUND())
    for n in [0, 1, 2, 3]:
        YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id=n))
    CLIENTS.close_all()
    GAME_TIMER.reset()
    send_state_to_ui()

    print("ENTERING END STATE")


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.SET_STATE)
def go_to_state(state):
    transitions = {
        STATE.SETUP: reset_match,
        STATE.AUTO: to_auto,
        STATE.TELEOP_1: to_teleop,
        STATE.END: to_end
    }
    if state in transitions:
        transitions[state]()
    else:
        print(f"Sorry, {state} is not a valid state to move to.")


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.SET_ROBOT_IP)
def set_robot_ip(ind, robot_ip):
    '''
    Sets the given client ip, and attempts to connect to it
    '''
    CLIENTS.connect_client(ind, robot_ip)


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.GET_MATCH_INFO)
def send_match_info_to_ui():
    '''
    Sends all match info to the UI
    '''
    YC.send(UI_HEADER.TEAMS_INFO(match_num=MATCH_NUMBER, teams=[
        ALLIANCES[ALLIANCE_COLOR.BLUE].robot1.info_dict(
            CLIENTS.clients[INDICES.BLUE_1].robot_ip),
        ALLIANCES[ALLIANCE_COLOR.BLUE].robot2.info_dict(
            CLIENTS.clients[INDICES.BLUE_2].robot_ip),
        ALLIANCES[ALLIANCE_COLOR.GOLD].robot1.info_dict(
            CLIENTS.clients[INDICES.GOLD_1].robot_ip),
        ALLIANCES[ALLIANCE_COLOR.GOLD].robot2.info_dict(
            CLIENTS.clients[INDICES.GOLD_2].robot_ip),
    ]))


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.GET_STATE)
def send_state_to_ui():
    '''
    Sends the GAME_STATE to the UI
    '''
    end_time, _ = GAME_TIMER.status()
    if GAME_STATE in STAGE_TIMES and end_time is not None:
        state_time = STAGE_TIMES.get(GAME_STATE)
        st = (end_time - state_time) * 1000
        YC.send(UI_HEADER.STATE(state=GAME_STATE,
                start_time=st, state_time=state_time))
    else:
        YC.send(UI_HEADER.STATE(state=GAME_STATE))


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.GET_CONNECTION_STATUS)
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
    CLIENTS.send_mode(AUTO if autonomous else TELEOP)


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.ROBOT_ON)
def enable_robot(ind):
    '''
    Send message to Runtime to enable the robot of team
    '''
    mode = AUTO if GAME_STATE == STATE.AUTO else TELEOP
    CLIENTS.clients[ind].send_mode(mode)


def disable_robots():
    '''
    Sends message to Runtime to disable all robots
    '''
    CLIENTS.send_mode(IDLE)


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.ROBOT_OFF)
def disable_robot(ind):
    '''
    Send message to Runtime to disable the robot of team
    '''
    CLIENTS.clients[ind].send_mode(IDLE)


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.DISCONNECT_ROBOT)
def disconnect_robot(ind):
    '''
    Send message to Runtime to disconnect the robot of team
    '''
    CLIENTS.clients[ind].close_connection()


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.UPDATE_ALLIANCE_SELECTION)
def update_alliance_selection(alliances: list):
    '''
    Updates the Google Sheets with the chosen alliances
    where 3 schools are in each alliance.
    '''
    # Sheet.write_alliance_selections(alliances)
    # print("Shepherd.py update alliance selection")
    # Sheet.write_alliance_selections(alliances)
    Sheet.write_alliance_selections(alliances)


###########################################
# Spring 2024 Game
###########################################
@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.SET_CHEAT_CODE)
def set_cheat_code(alliance, CHEAT_CODE):
    if alliance == ALLIANCE_COLOR.BLUE:
        global BLUE_CHEAT_CODE
        BLUE_CHEAT_CODE = CHEAT_CODE
    else:
        global GOLD_CHEAT_CODE
        GOLD_CHEAT_CODE = CHEAT_CODE
    if BLUE_CHEAT_CODE and GOLD_CHEAT_CODE:
        YC.send(UI_HEADER.SET_CHEAT_CODE(BLUE_CHEAT_CODE, GOLD_CHEAT_CODE))


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.UPDATE_SECURITY_BREACH_SCORE)
def update_security_breach_score(alliance, done):
    '''
    Updates the security breach score and send updated score to sheet
    '''

    Sheet.write_security_breach(MATCH_NUMBER, alliance, done)


@SHEPHERD_HANDLER.EVERYWHERE.on(SHEPHERD_HEADER.UPDATE_CHEAT_CODE_SCORE)
def update_cheat_code_score(alliance, score):
    '''
    Updates the cheat code score and send updated score to sheet

    '''

    Sheet.write_cheat_code(MATCH_NUMBER, alliance, score)


###########################################
# Event to Function Mappings for each Stage
###########################################
# pylint: disable=no-member
if __name__ == '__main__':
    threading.Thread(target=pull_from_sheets, daemon=True).start()
    start()
