
class YDL_TARGETS():
    SHEPHERD = "ydl_target_shepherd"
    UI = "ydl_target_ui"
    SENSORS = "ydl_target_sensors"


# pylint: disable=invalid-name
class SHEPHERD_HEADER():
    GET_MATCH_INFO = "get_match_info"
    # GET_MATCH_INFO{}
    # source: UI. Asks Shepherd what match info is currently cached.
    
    SET_MATCH_NUMBER = "set_match_number"
    # SET_MATCH_NUMBER{match_num}: 
    # source: UI. Sets the match number. Shepherd then fetches
    # information for that match and sends it to the UI.

    SETUP_MATCH = "setup_match"
    # SETUP_MATCH{team_name, team_num, match_num}
    # SETUP_MATCH{b1name, b1#, b2name, b2#, g1name, g1#, g2name, g2#, match#}:
    # sets up the match given all the match info

    RESET_MATCH = "reset_match"
    # RESET_MATCH{}
    # source: UI. Resets the match, moving back to setup.

    GET_SCORES = "get_scores"
    # GET_SCORES{}: 
    # source: UI. Asks Shepherd what the current scores are.

    SET_SCORES = "set_scores"
    # SET_SCORES{blue_score, gold_score}: 
    # source: UI. adjusts the current scores to the input scores.

    GET_STATE = "get_state"
    # GET_STATE{}
    # source: UI. Asks Shepherd what the current game state is.

    SET_STATE = "set_state"
    # SET_STATE{state}
    # source: UI. Sets the game state.
    
    START_NEXT_STAGE = "start_next_stage"
    # START_NEXT_STAGE{}: starts the next stage

    RESET_CURRENT_STAGE = "reset_current_stage"
    # RESET_CURRENT_STAGE{}: resets the current stage
    
    STAGE_TIMER_END = "stage_timer_end"
    # STAGE_TIMER_END{}: 
    # source: Timer. Sent when a stage timer has ended.
    
    GET_CONNECTION_STATUS = "get_connection_status"
    # GET_CONNECTION_STATUS{}:
    # source: UI. Asks Shepherd to send robot connection statuses to UI.
    
    SET_ROBOT_IP = "set_robot_ip"
    # SET_ROBOT_IP{team_number, ip}
    # source: UI. Attempts to connect team to robot with given ip.

    ROBOT_OFF = "robot_off"
    # ROBOT_OFF{team_number}: 
    # source: UI. Takes in team number and disables their robot.

    ROBOT_ON = "robot_on"
    # ROBOT_ON{team_number}: 
    # source: UI. Takes in team number and enables their robot.

# pylint: disable=invalid-name




class UI_HEADER():
    """
    These are headers used by Shepherd to send information to the Staff UI.
    """
    ALL_INFO = "all_info"
    # ALL_INFO{}
    # used for match recovery
    TEAMS_INFO = "teams_info"
    # TEAMS_INFO{match_num, round_num, team_num, team_name, custom_ip, tinder, buttons}
    # info about teams
    SCORES = "scores"
    # SCORES{ TODO: interface }
    ROBOT_CONNECTION = "robot_connection"
    # CONNECTIONS{team_num: int, connected: bool, ip}
    STATE = "state"
    # STATE{state}
    # tells UI that Shepherd is now in this state
    # TODO: is this redundant with teams_info?
    RESET_TIMERS = "reset_timers"
    # RESET_TIMERS{}


class SENSOR_HEADER():
    """
    Headers used for Shepherd to send messages to the Sensor Interface.
    """
    # EXAMPLE_HEADER = "example_header"
    pass

# pylint: disable=invalid-name






# A dictionary of pages -> whether page is password protected
# password.html should not be included in this list, since
# server.py will just route to that automatically
# add additional pages here

UI_PAGES = {
    "scoreboard.html": False,
    "score_adjustment.html": True,
    "staff_gui.html": True,
    "match_recovery.html": True,
    "ref_gui.html": True
}



class CONSTANTS():
    AUTO_TIME = 10
    TELEOP_TIME = 10
    SPREADSHEET_ID = "[todo: fill with dummy spreadsheet]"
    CSV_FILE_NAME = "sheets/sc2021.csv"

# pylint: disable=invalid-name


class ALLIANCE_COLOR():
    GOLD = "gold"
    BLUE = "blue"


# pylint: disable=invalid-name


class TIMER_TYPES():
    MATCH = {"TYPE": "match", "FUNCTION": SHEPHERD_HEADER.STAGE_TIMER_END}

# pylint: disable=invalid-name


class STATE():
    SETUP = "setup"
    AUTO = "auto"
    TELEOP = "teleop"
    END = "end"


class PROTOBUF_TYPES():
    RUN_MODE = 0
    START_POS = 1
    CHALLENGE_DATA = 2  # text proto
    LOG = 3  # text proto
    DEVICE_DATA = 4
    GAME_STATE = 5
