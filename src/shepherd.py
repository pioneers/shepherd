import threading
import time
# commenting out simple audio code
# import simpleaudio as sa
from ydl import YDLClient
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
YC = YDLClient(YDL_TARGETS.SHEPHERD)
MATCH_NUMBER: int = -1
GAME_STATE: str = STATE.END
TIMERS = TimerGroup()
GAME_TIMER = Timer(TIMERS,
    lambda: YC.send(SHEPHERD_HEADER.STAGE_TIMER_END()))
BLIZZARD_WARNING_TIMER = Timer(TIMERS,
    lambda: YC.send(SHEPHERD_HEADER.SOUND_BLIZZARD_WARNING()))

ALLIANCES = {
    ALLIANCE_COLOR.GOLD: Alliance(Robot("", -1), Robot("", -1)),
    ALLIANCE_COLOR.BLUE: Alliance(Robot("", -1), Robot("", -1)),
}

CLIENTS = RuntimeClientManager(YC)


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
    while True:
        payload = YC.receive()
        print("GAME STATE OUTSIDE: ", GAME_STATE)
        print(payload)

        if GAME_STATE in FUNCTION_MAPPINGS:
            func_list = FUNCTION_MAPPINGS.get(GAME_STATE)
            func = func_list.get(payload[1]) or EVERYWHERE_FUNCTIONS.get(payload[1])
            if func is not None:
                func(**payload[2]) #deconstructs dictionary into arguments
            else:
                print(f"Invalid Event in {GAME_STATE}")
        else:
            print(f"Invalid State: {GAME_STATE}")

def pull_from_sheets():
    while True:
        if not TIMERS.is_paused() and GAME_STATE not in [STATE.END, STATE.SETUP]:
            Sheet.send_scores_for_icons(MATCH_NUMBER)
        time.sleep(2.0)


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

def pause_timer():
    '''
    Pauses a running match. Invalid to call during setup and end.
    '''
    if not TIMERS.is_paused():
        TIMERS.pause()
        disable_robots()
        YC.send(UI_HEADER.PAUSE_TIMER())

def resume_timer():
    '''
    Resumes a running match. Invalid to call during setup and end.
    '''
    if TIMERS.is_paused():
        TIMERS.resume()
        enable_robots(autonomous=(GAME_STATE==STATE.AUTO))
        end_time, _ = GAME_TIMER.status()
        YC.send(UI_HEADER.RESUME_TIMER(end_time=end_time, pause_end=time.time()))


###########################################
# Transition Methods
###########################################


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
    send_score_to_ui()
    send_state_to_ui()
    print(f"ENTERING {state} STATE")

def to_auto():
    '''
    Move to the autonomous stage where robots should begin autonomously.
    By the end, should be in autonomous state, allowing any function from this
    stage to be called and autonomous match timer should have begun.
    '''
    GAME_TIMER.start(STAGE_TIMES[STATE.AUTO])
    enable_robots(autonomous=True)
    play_sound("static/boxing-bell.wav")
    for n in [0,1,2,3]:
        YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id=n))
    set_state(STATE.AUTO)

def to_teleop_1():
    GAME_TIMER.start(STAGE_TIMES[STATE.TELEOP_1])
    BLIZZARD_WARNING_TIMER.start(CONSTANTS.BLIZZARD_WARNING_TIME)
    enable_robots(autonomous=False)
    set_state(STATE.TELEOP_1)

def to_blizzard():
    GAME_TIMER.start(STAGE_TIMES[STATE.BLIZZARD])
    enable_robots(autonomous=False)
    set_state(STATE.BLIZZARD)
    YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id=4))
    YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id=5))

def to_teleop_2():
    GAME_TIMER.start(STAGE_TIMES[STATE.TELEOP_2])
    enable_robots(autonomous=False)
    set_state(STATE.TELEOP_2)
    YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id=4))
    YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id=5))

def to_endgame():
    GAME_TIMER.start(STAGE_TIMES[STATE.ENDGAME])
    enable_robots(autonomous=False)
    set_state(STATE.ENDGAME)

def to_end():
    '''
    Go to the end state, finishing the game and flushing scores to the spreadsheet.
    '''
    global GAME_STATE
    GAME_STATE = STATE.END
    disable_robots()
    play_sound("static/trim.wav")
    for n in [0,1,2,3]:
        YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id=n))
    CLIENTS.close_all()
    GAME_TIMER.reset()
    send_state_to_ui()
    send_score_to_ui()
    flush_scores()

    # temporary code for scrimmage, comment later
    Sheet.write_scores_from_read_scores(MATCH_NUMBER)

    print("ENTERING END STATE")


def go_to_state(state):
    transitions = {
        STATE.SETUP: reset_match,
        STATE.AUTO: to_auto,
        STATE.TELEOP_1: to_teleop_1,
        STATE.BLIZZARD: to_blizzard,
        STATE.TELEOP_2: to_teleop_2,
        STATE.ENDGAME: to_endgame,
        STATE.END: to_end
    }
    if state in transitions:
        transitions[state]()
    else:
        print(f"Sorry, {state} is not a valid state to move to.")




def set_robot_ip(ind, robot_ip):
    '''
    Sets the given client ip, and attempts to connect to it
    '''
    CLIENTS.connect_client(ind, robot_ip)


def score_adjust(blue_score=None, gold_score=None):
    '''
    Allow for score to be changed based on referee decisions
    '''
    if blue_score is not None:
        ALLIANCES[ALLIANCE_COLOR.BLUE].set_score(int(blue_score))
    if gold_score is not None:
        ALLIANCES[ALLIANCE_COLOR.GOLD].set_score(int(gold_score))
    send_score_to_ui()
    flush_scores()

    # temporary code for exhibition, remove later
    YC.send(UI_HEADER.SCORES(
        blue_score=ALLIANCES[ALLIANCE_COLOR.BLUE].score,
        gold_score=ALLIANCES[ALLIANCE_COLOR.GOLD].score
    ))


def flush_scores():
    '''
    Sends the most recent match score to the spreadsheet if connected to the internet
    '''
    # temporary code for exhibition, uncomment later
    # Sheet.write_scores(
    #     MATCH_NUMBER,
    #     ALLIANCES[ALLIANCE_COLOR.BLUE].score,
    #     ALLIANCES[ALLIANCE_COLOR.GOLD].score
    # )


def send_match_info_to_ui():
    '''
    Sends all match info to the UI
    '''
    YC.send(UI_HEADER.TEAMS_INFO(match_num=MATCH_NUMBER, teams=[
        ALLIANCES[ALLIANCE_COLOR.BLUE].robot1.info_dict(CLIENTS.clients[INDICES.BLUE_1].robot_ip),
        ALLIANCES[ALLIANCE_COLOR.BLUE].robot2.info_dict(CLIENTS.clients[INDICES.BLUE_2].robot_ip),
        ALLIANCES[ALLIANCE_COLOR.GOLD].robot1.info_dict(CLIENTS.clients[INDICES.GOLD_1].robot_ip),
        ALLIANCES[ALLIANCE_COLOR.GOLD].robot2.info_dict(CLIENTS.clients[INDICES.GOLD_2].robot_ip),
    ]))


def send_score_to_ui():
    '''
    Sends the current score to the UI
    '''
    # temporary code for exhibition, uncomment later
    # YC.send(UI_HEADER.SCORES(
    #     blue_score=ALLIANCES[ALLIANCE_COLOR.BLUE].score,
    #     gold_score=ALLIANCES[ALLIANCE_COLOR.GOLD].score
    # ))


def send_state_to_ui():
    '''
    Sends the GAME_STATE to the UI
    '''
    end_time, _ = GAME_TIMER.status()
    if GAME_STATE in STAGE_TIMES and end_time is not None:
        state_time = STAGE_TIMES.get(GAME_STATE)
        st = (end_time - state_time) * 1000
        YC.send(UI_HEADER.STATE(state=GAME_STATE, start_time=st, state_time=state_time))
    else:
        YC.send(UI_HEADER.STATE(state=GAME_STATE))


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


def disable_robot(ind):
    '''
    Send message to Runtime to disable the robot of team
    '''
    CLIENTS.clients[ind].send_mode(IDLE)


def disconnect_robot(ind):
    '''
    Send message to Runtime to disconnect the robot of team
    '''
    CLIENTS.clients[ind].close_connection()


def update_alliance_selection(alliances: list):
    '''
    Updates the Google Sheets with the chosen alliances
    where 3 schools are in each alliance.
    '''
    Sheet.write_alliance_selections(alliances)


###########################################
# Spring 2022 Game
###########################################


def sound_blizzard_warning():
    # play_sound("static/blizzard_warning.wav")
    pass

def play_sound(filename):
    # threading.Thread(target=actually_make_sound, args=(filename,)).start()
    pass

def actually_make_sound(filename):
    # commenting out simple audio code
    # wave_obj = sa.WaveObject.from_wave_file(filename)
    # play_obj = wave_obj.play()
    # play_obj.wait_done()
    pass


def forward_button_light(num, type, on):
    if type == "button":
        if on:
            YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id=num))
        else:
            YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id=num))
    # if type == "midline":
    #     if on:
    #         YC.send(SENSOR_HEADER.TURN_ON_MIDLINE(id=0))
    #         YC.send(SENSOR_HEADER.TURN_ON_MIDLINE(id=1))


def flash_lights(ar):
    for _ in range(2):
        for a in ar:
            YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id=a))
        time.sleep(0.25)
        for a in ar:
            YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id=a))
        time.sleep(0.25)


def button_pressed(button):
    id = button
    print(f"Detected button {id} pressed")
    ar = [0,1] if id == 0 else [2,3]
    threading.Thread(target=flash_lights, args=(ar,)).start()



###########################################
# Event to Function Mappings for each Stage
###########################################

# pylint: disable=no-member
FUNCTION_MAPPINGS = {
    STATE.SETUP: {
        SHEPHERD_HEADER.SET_MATCH_NUMBER.name: set_match_number,
        SHEPHERD_HEADER.SET_TEAMS_INFO.name: set_teams_info,
        SHEPHERD_HEADER.SETUP_MATCH.name: to_setup,
        SHEPHERD_HEADER.START_NEXT_STAGE.name: to_auto,
    },
    STATE.AUTO: {
        SHEPHERD_HEADER.STAGE_TIMER_END.name: to_teleop_1,
        # SHEPHERD_HEADER.RESET_CURRENT_STAGE.name: to_auto,
        # SHEPHERD_HEADER.START_NEXT_STAGE.name: to_teleop,
    },
    STATE.TELEOP_1: {
        SHEPHERD_HEADER.SOUND_BLIZZARD_WARNING.name: sound_blizzard_warning,
        SHEPHERD_HEADER.STAGE_TIMER_END.name: to_blizzard,
    },
    STATE.BLIZZARD: {
        SHEPHERD_HEADER.STAGE_TIMER_END.name: to_teleop_2,
    },
    STATE.TELEOP_2: {
        SHEPHERD_HEADER.STAGE_TIMER_END.name: to_endgame,
    },
    STATE.ENDGAME: {
        SHEPHERD_HEADER.STAGE_TIMER_END.name: to_end,
    },
    STATE.END: {
        SHEPHERD_HEADER.SET_MATCH_NUMBER.name: set_match_number,
        SHEPHERD_HEADER.SET_TEAMS_INFO.name: set_teams_info,
        SHEPHERD_HEADER.SETUP_MATCH.name: to_setup,
        # temporary code for exhibition, uncomment later
        # SHEPHERD_HEADER.SET_SCORES.name: score_adjust,
    }
}

EVERYWHERE_FUNCTIONS = {
    SHEPHERD_HEADER.GET_MATCH_INFO.name: send_match_info_to_ui,
    SHEPHERD_HEADER.GET_SCORES.name: send_score_to_ui,
    SHEPHERD_HEADER.GET_STATE.name: send_state_to_ui,
    SHEPHERD_HEADER.GET_CONNECTION_STATUS.name: send_connection_status_to_ui,

    SHEPHERD_HEADER.SET_STATE.name: go_to_state,
    SHEPHERD_HEADER.ROBOT_OFF.name: disable_robot,
    SHEPHERD_HEADER.ROBOT_ON.name: enable_robot,
    SHEPHERD_HEADER.SET_ROBOT_IP.name: set_robot_ip,
    SHEPHERD_HEADER.DISCONNECT_ROBOT.name: disconnect_robot,
    SHEPHERD_HEADER.RESET_MATCH.name: reset_match,

    SHEPHERD_HEADER.TURN_LIGHT_FROM_UI.name: forward_button_light,
    SHEPHERD_HEADER.BUTTON_PRESS.name: button_pressed,
    SHEPHERD_HEADER.PAUSE_TIMER.name: pause_timer,
    SHEPHERD_HEADER.RESUME_TIMER.name: resume_timer,
    # SHEPHERD_HEADER.TURN_BUTTON_LIGHT_FROM_UI.name: forward_button_light,
    # SHEPHERD_HEADER.UPDATE_SCORE.name: update_score,
    # temporary code for exhibition, remove later
    SHEPHERD_HEADER.SET_SCORES.name: score_adjust,
    SHEPHERD_HEADER.UPDATE_ALLIANCE_SELECTION.name: update_alliance_selection,
}

if __name__ == '__main__':
    threading.Thread(target=pull_from_sheets, daemon=True).start()
    start()
