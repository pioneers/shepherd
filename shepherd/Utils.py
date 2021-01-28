# pylint: disable=invalid-name
class SHEPHERD_HEADER():
    START_NEXT_STAGE = "start_next_stage"
    # START_NEXT_STAGE{}: starts the next stage

    RESET_CURRENT_STAGE = "reset_current_stage"
    # RESET_CURRENT_STAGE{}: resets the current stage

    # TODO: revisit
    RESET_MATCH = "reset_match"
    # RESET_MATCH{}: resets the current match

    # TODO: do
    RESET_ROUND = "reset_round"
    # RESET_ROUND{}: resets the current round, preserving relevant state from the previous round.

    # TODO: make work for 2021
    GET_ROUND_INFO = "get_round_info"
    # GET_ROUND_INFO{match_num, round_num}: gets match info for given match number

    # TODO: fix for 2021
    SETUP_MATCH = "setup_match"
    # SETUP_MATCH{b1name, b1#, b2name, b2#, g1name, g1#, g2name, g2#, match#}:
    # sets up the match given the corresponding info about the teams and match number
    # also has {g1_custom_ip, g2_custom_ip, b1_custom_ip, b2_custom_ip}

    # TODO: do
    SETUP_ROUND = "setup_round"
    # SETUP_ROUND{teamname, team#, match#, round#, tinder, buttons}

    GET_CONNECTION_STATUS = "get_connection_status"
    # GET_CONNECTION_STATUS{}: requested from the Staff UI to check robot
    # connection statuses

    SET_GAME_INFO = "set_game_info"
    # SET_GAME_INFO{}: sets tinder/activated buttons

    GET_MATCH_INFO = "get_match_info"
    # GET_MATCH_InFO{}: sends match info to the UI

    UPDATE_TINDER = "update_tinder"
    # UPDATE_TINDER{tinder}: updates the amount of tinder

    GET_SCORES = "get_scores"
    # GET_SCORES{}: get time and penalty time of robot

    SCORE_ADJUST = "score_adjust"
    # SCORE_ADJUST{time, penalty}: adjusts the current scores to the input scores

    STAGE_TIMER_END = "stage_timer_end"
    # STAGE_TIMER_END{}: ends the stage's timer

    ROBOT_OFF = "robot_off"
    # ROBOT_OFF{team_number}: takes in team number and disables their robot

    END_EXTENDED_TELEOP = "end_extended_teleop"
    # END_EXTENDED_TELEOP{}: ends the extended teloperated period

    CODE_RETRIEVAL = "code_retrieval"
    # CODE_RETRIEVAL{alliance, result}: retrieves code (from sensors.py)

    CODE_APPLICATION = "code_application"
    # CODE_APPLICATION{alliance, result}: applies code (from sensors.py)

    MASTER_ROBOT = "master_robot"

    FINAL_SCORE = "final_score"
    ASSIGN_TEAMS = "assign_teams"
    # ASSIGN_TEAMS{g1num, g2num, b1num, b2num}
    TEAM_RETRIEVAL = "team_retrieval"
    # TEAM_RETRIEVAL{}

    ROBOT_CONNECTION_STATUS = "robot_connection_status"
    # ROBOT_CONNECTION_STATUS{team_number, connection[True/False]}

    REQUEST_CONNECTIONS = "request_connections"
    # REQUEST_CONNECTIONS{}

    # AUTO

    AUTO_TRACK_COMPLETE = "auto_track_complete"

    # CITY

    STOPLIGHT_TIMER_END = "stoplight_timer_end"
    STOPLIGHT_BUTTON_PRESS = "stoplight_button_press"
    STOPLIGHT_PENALTY = "stoplight_penalty"
    FOREST_ENTRY = "forest_entry"

    # FOREST
    CONTACT_WALL = "contact_wall"
    # CONTACT_WALL{}: wall was contacted
    DESERT_ENTRY = "desert_entry"

    # DESERT
    SANDSTORM_TIMER_END = "sandstorm_timer_end"
    DEHYDRATION_ENTRY = "dehydration_entry"

    # DEHYDRATION
    DEHYDRATION_BUTTON_PRESS = "dehydration_button_press"
    DEHYDRATION_TIMER_END = "dehydration_timer_end"
    ROBOT_DEHYDRATED_TIMER_END = "robot_dehydrated_timer_end"

    # FIRE
    COLLECT_TINDER = "collect_tinder"
    HYPOTHERMIA_ENTRY = "hypothermia_entry"
    TOGGLE_FIRE = "toggle_fire"

    # HYPOTHERMIA
    FINAL_ENTRY = "to_final"

    # AIRPORT
    CROSS_FINISH_LINE = "to_end"

# pylint: disable=invalid-name


class DAWN_HEADER():
    CODES = "codes"
    DECODE = "decode"
    SPECIFIC_ROBOT_STATE = "srt"
    MASTER = "master"
    IP_ADDRESS = "ip_address"
    ROBOT_STATE = "rs"
    HEARTBEAT = "heartbeat"
    RESET = "reset"
    # TODO this^


class RUNTIME_HEADER():
    SPECIFIC_ROBOT_STATE = "specific_robot_state"
    # SPECIFIC_ROBOT_STATE{team_number, autonomous, enabled}
    # robot ip is 192.168.128.teamnumber
    DECODE = "decode"
    # DECODE{team_number, seed}
    REVERSE_TEN_SECONDS = "reverse_ten_seconds"
    START_ROBOT = "start_robot"
    STOP_ROBOT = "stop_robot"

# pylint: disable=invalid-name


class UI_HEADER():
    """
    These are headers used by Shepherd to send information to the Staff UI.
    """
    TEAMS_INFO = "teams_info"
    SCORES = "scores"
    # SCORES{time[seconds], penalty[seconds], score[seconds], stamp_time[seconds]}
    # TODO: update for one robot
    CONNECTIONS = "connections"  # TODO: ask Matt why this function is commented out
    # CONNECTIONS{robot_connection[True/False]}
    GAME_INFO = "game_info"
    # GAME_INFO{tinder, buttons activated}
    SENSORS_INFO = "sensors_info"
    # SENSORS_INFO{tinder}

# pylint: disable=invalid-name


class SCOREBOARD_HEADER():
    """
    These are headers used by Shepherd to send information to the Scoreboard.
    """
    SCORES = "scores"
    # SCORES{time, penalty}
    TEAM = "team"
    # TEAM{teamname, team#}
    STAGE = "stage"
    # STAGE{stage}
    STAGE_TIMER_START = "stage_timer_start"
    STAGE_TIMER_STOP = "stage_timer_stop"
    RESET_TIMERS = "reset_timers"
    ALL_INFO = "all_info"


class TABLET_HEADER():
    TEAMS = "teams"
    #{b1num, b2num, g1num, g2num}
    CODE = "code"
    #{alliance, code}
    COLLECT_CODES = "collect_codes"
    # {}
    RESET = "reset"
    # {}

# pylint: disable=invalid-name


class CONSTANTS():
    AUTO_TIME = 5  # 20
    TELEOP_TIME = 10  # 280
    STOPLIGHT_TIME = 5  # 30
    SANDSTORM_COVER_TIME = 10
    DEHYRATION_TIME = 30
    ROBOT_DEHYDRATED_TIME = 10
    SPREADSHEET_ID = "1vurNOrlIIeCHEtK5aJVDfHrRM1AC2qWvIbtWqUgnmLk"
    CSV_FILE_NAME = "Sheets/fc2019.csv"
    STUDENT_DECODE_TIME = 1

# pylint: disable=invalid-name


class ALLIANCE_COLOR():
    GOLD = "gold"
    BLUE = "blue"

# pylint: disable=invalid-name


class LCM_TARGETS():
    SHEPHERD = "lcm_target_shepherd"
    SCOREBOARD = "lcm_target_scoreboard"
    SENSORS = "lcm_target_sensors"
    UI = "lcm_target_ui"
    DAWN = "lcm_target_dawn"
    RUNTIME = "lcm_target_runtime"
    TABLET = "tablet"

# pylint: disable=invalid-name


class TIMER_TYPES():
    MATCH = {"TYPE": "match", "NEEDS_FUNCTION": True,
             "FUNCTION": SHEPHERD_HEADER.STAGE_TIMER_END}
    STUDENT_DECODE = {"TYPE": "student_decode", "NEEDS_FUNCTION": True,
                      "FUNCTION": SHEPHERD_HEADER.CODE_RETRIEVAL}
    STOPLIGHT_WAIT = {"TYPE": "stoplight_wait", "NEEDS_FUNCTION": True,
                      "FUNCTION": SHEPHERD_HEADER.STOPLIGHT_TIMER_END}  # this should be a sensor header to turn the stoplight green
    SANDSTORM_COVER = {"TYPE": "sandstorm_cover", "NEEDS_FUNCTION": True,
                       "FUNCTION": SHEPHERD_HEADER.SANDSTORM_TIMER_END}
    DEHYDRATION = {"TYPE": "dehydrated", "NEEDS_FUNCTION": True,
                   "FUNCTION": SHEPHERD_HEADER.DEHYDRATION_TIMER_END}
    ROBOT_DEHYDRATED = {"TYPE": "robot_dehydrated", "NEEDS_FUNCTION": True,
                        "FUNCTION": SHEPHERD_HEADER.ROBOT_DEHYDRATED_TIMER_END}

# pylint: disable=invalid-name


class STATE():
    SETUP = "setup"
    AUTO = "auto"
    CITY = "city"
    FOREST = "forest"
    SANDSTORM = "sandstorm"
    DEHYDRATION = "dehydration"
    FIRE = "fire"
    HYPOTHERMIA = "hypothermia"
    FINAL = "final"
    END = "end"


class PROTOBUF_TYPES():
    RUN_MODE = 0
    START_POS = 1
    CHALLENGE_DATA = 2  # text proto
    LOG = 3  # text proto
    DEVICE_DATA = 4
    GAME_STATE = 5
