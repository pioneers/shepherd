# pylint: disable=invalid-name

class YDL_TARGETS():
    SHEPHERD = "ydl_target_shepherd"
    UI = "ydl_target_ui"
    SENSORS = "ydl_target_sensors"


# for headers, [field] denotes an optional field

class SHEPHERD_HEADER():
    GET_MATCH_INFO = "get_match_info"
    # GET_MATCH_INFO{}
    # source: UI. Asks Shepherd what match info is currently cached.

    SET_MATCH_NUMBER = "set_match_number"
    # SET_MATCH_NUMBER{match_num}
    # source: UI. Sets the match number. Shepherd then fetches
    # information for that match and sends it to the UI.

    SET_TEAMS_INFO = "set_teams_info"
    # SET_TEAMS_INFO{teams}
    # teams = 4*{team_name, team_num, robot_ip, [starting_position]}
    # source: Sheet. Sets the match info, which has been fetched from a spreadsheet

    SETUP_MATCH = "setup_match"
    # SETUP_MATCH{match_num, teams}
    # sets up the match given all the match info

    RESET_MATCH = "reset_match"
    # RESET_MATCH{}
    # source: UI. Resets the match, moving back to setup.

    GET_SCORES = "get_scores"
    # GET_SCORES{}
    # source: UI. Asks Shepherd what the current scores are.

    SET_SCORES = "set_scores"
    # SET_SCORES{[blue_score], [gold_score]}
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
    # SET_ROBOT_IP{ind, robot_ip}
    # source: UI. Attempts to connect team to robot with given ip.

    ROBOT_OFF = "robot_off"
    # ROBOT_OFF{ind}:
    # source: UI. Takes in index and disables their robot.

    ROBOT_ON = "robot_on"
    # ROBOT_ON{ind}:
    # source: UI. Takes in index and enables their robot.




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
    # ROBOT_CONNECTION{ind: int, connected: bool, robot_ip: str}
    STATE = "state"
    # STATE{state, [start_time]}
    # tells UI that Shepherd is now in this state
    # TODO: is this redundant with teams_info?
    RESET_TIMERS = "reset_timers"
    # RESET_TIMERS{}


class SENSOR_HEADER():
    """
    Headers used for Shepherd to send messages to the Sensor Interface.
    """
    # EXAMPLE_HEADER = "example_header"








# A dictionary of pages -> whether page is password protected
# password.html should not be included in this list, since
# server.py will just route to that automatically
# add additional pages here

UI_PAGES = {
    "scoreboard.html": False,
    "score_adjustment.html": True,
    "staff_gui.html": True,
    "match_recovery.html": True,
    "ref_gui.html": True,
    "match_creator.html": True,
    "alliance_selection.html": True,
    "bracket_ui.html": False,
}



class CONSTANTS():
    AUTO_TIME = 10
    TELEOP_TIME = 10
    CSV_FILE_NAME = "sheets/Shepherd Evergreen Database - Match Database.csv"
    SPREADSHEET_ID = "1JCtt_Iqyx15EOAZN6agqeeUKCFsrL6oOy3brKyAWjBM"
    UI_PASSWORD_HASH = "44590c963be2a79f52c07f7a7572b3907bf5bb180d993bd31aab510d29bbfbd3"


class ALLIANCE_COLOR():
    GOLD = "gold"
    BLUE = "blue"


class INDICES():
    BLUE_1 = 0
    BLUE_2 = 1
    GOLD_1 = 2
    GOLD_2 = 3






class TIMER_TYPES():
    MATCH = {"TYPE": "match", "FUNCTION": SHEPHERD_HEADER.STAGE_TIMER_END}



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
