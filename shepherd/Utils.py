# pylint: disable=invalid-name
class SHEPHERD_HEADER():
    START_NEXT_STAGE = "start_next_stage"
    # START_NEXT_STAGE{}: starts the next stage

    RESET_CURRENT_STAGE = "reset_current_stage"
    # RESET_CURRENT_STAGE{}: resets the current stage

    RESET_MATCH = "reset_match"
    # RESET_MATCH{}: resets the current match

    SETUP_MATCH = "setup_match"
    # SETUP_MATCH{team_name, team_num, match_num}
    # SETUP_MATCH{b1name, b1#, b2name, b2#, g1name, g1#, g2name, g2#, match#}:
    # sets up the match given the corresponding info about the teams and match number
    # also has {g1_custom_ip, g2_custom_ip, b1_custom_ip, b2_custom_ip}


    GET_CONNECTION_STATUS = "get_connection_status"
    # GET_CONNECTION_STATUS{}: requested from the Staff UI to check robot
    # connection statuses

    SET_CUSTOM_IP = "set_custom_ip"
    # TODO: interface

    GET_MATCH_INFO = "get_match_info"
    # GET_MATCH_InFO{}: sends match info to the UI

    GET_MATCH_INFO_NO_ARGS = "get_match_info_no_args"
    # gets cached match info (called on UI page load)

    GET_SCORES = "get_scores"
    # GET_SCORES{}: get time, penalty and stamps of robot

    SCORE_ADJUST = "score_adjust"
    # SCORE_ADJUST{time, penalty, stamp_time}: adjusts the current scores to the input scores. Total time is time + penalty + stamp time

    STAGE_TIMER_END = "stage_timer_end"
    # STAGE_TIMER_END{}: ends the stage's timer

    ROBOT_OFF = "robot_off"
    # ROBOT_OFF{team_number}: takes in team number and disables their robot

    ROBOT_ON = "robot_on"
    # ROBOT_ON{team_number}: takes in team number and enables their robot

    REQUEST_CONNECTIONS = "request_connections"
    # REQUEST_CONNECTIONS{}

    GET_STATE = "get_state"
    # GET_STATE{}

    SET_STATE = "set_state"
    # SET_STATE{ state }

# pylint: disable=invalid-name




class UI_HEADER():
    """
    These are headers used by Shepherd to send information to the Staff UI.
    """
    ALL_INFO = "all_info"
    # ALL_INFO{}
    TEAMS_INFO = "teams_info"
    # TEAMS_INFO{match_num, round_num, team_num, team_name, custom_ip, tinder, buttons}
    SCORES = "scores"
    # SCORES{ TODO: interface }
    ROBOT_CONNECTION = "robot_connection"
    # CONNECTIONS{team_num: int, connected: bool, ip}
    STAGE = "stage"
    # STAGE{stage, start_time}
    # start_time = timestamp
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
    "stage_control.html": True,
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


class YDL_TARGETS():
    SHEPHERD = "ydl_target_shepherd"
    SENSORS = "ydl_target_sensors"
    UI = "ydl_target_ui"

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
