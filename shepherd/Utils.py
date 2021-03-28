# pylint: disable=invalid-name
class SHEPHERD_HEADER():
    START_NEXT_STAGE = "start_next_stage"
    # START_NEXT_STAGE{}: starts the next stage

    RESET_CURRENT_STAGE = "reset_current_stage"
    # RESET_CURRENT_STAGE{}: resets the current stage

    RESET_MATCH = "reset_match"
    # RESET_MATCH{}: resets the current match

    RESET_ROUND = "reset_round"
    # RESET_ROUND{}: resets the current round, preserving relevant state from the previous round.

    GET_ROUND_INFO = "get_round_info"
    # GET_ROUND_INFO{match_num, round_num}: gets match info for given match number

    GET_ROUND_INFO_NO_ARGS = "get_round_info_no_args"
    # GET_ROUND_INFO_NO_ARGS{}: gets cached match info (called on UI page load)

    SETUP_MATCH = "setup_match"
    # SETUP_MATCH{team_name, team_num, match_num}
    # SETUP_MATCH{b1name, b1#, b2name, b2#, g1name, g1#, g2name, g2#, match#}:
    # sets up the match given the corresponding info about the teams and match number
    # also has {g1_custom_ip, g2_custom_ip, b1_custom_ip, b2_custom_ip}

    SETUP_ROUND = "setup_round"
    # SETUP_ROUND{teamname, team#, match#, round#, tinder, buttons}

    GET_CONNECTION_STATUS = "get_connection_status"
    # GET_CONNECTION_STATUS{}: requested from the Staff UI to check robot
    # connection statuses

    SET_CUSTOM_IP = "set_custom_ip"
    # SET_CUSTOM_IP{custom_ip: str}

    SET_GAME_INFO = "set_game_info"
    # SET_GAME_INFO{}: sets tinder/activated buttons

    GET_MATCH_INFO = "get_match_info"
    # GET_MATCH_InFO{}: sends match info to the UI

    UPDATE_TINDER = "update_tinder"
    # UPDATE_TINDER{tinder}: updates the amount of tinder

    GET_SCORES = "get_scores"
    # GET_SCORES{}: get time, penalty and stamps of robot

    SCORE_ADJUST = "score_adjust"
    # SCORE_ADJUST{time, penalty, stamp_time}: adjusts the current scores to the input scores. Total time is time + penalty + stamp time

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

    GET_BIOME = "get_biome"
    # GET_BIOME{}

    SET_BIOME = "set_biome"
    # GET_BIOME{biome: str}

    # AUTO
    CITY_LINEBREAK = "city_linebreak"

    # CITY
    STOPLIGHT_TIMER_END = "stoplight_timer_end"
    STOPLIGHT_BUTTON_PRESS = "stoplight_button_press"
    STOPLIGHT_PENALTY = "stoplight_penalty"
    STOPLIGHT_CROSS = "stoplight_cross"
    DRAWBRIDGE_SHORTCUT = "drawbridge_shortcut" #could be in city or forest
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
    # DEHYDRATION_BUTTON_PRESS{button: int}
    DEHYDRATION_TIMER_END = "dehydration_timer_end"
    ROBOT_DEHYDRATED_TIMER_END = "robot_dehydrated_timer_end"

    # FIRE
    # SET_TINDER{tinder: int}
    SET_TINDER = "set_tinder"
    HYPOTHERMIA_ENTRY = "hypothermia_entry"
    FIRE_LEVER = "fire_lever"

    # HYPOTHERMIA
    FINAL_ENTRY = "to_final"

    # AIRPORT

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
    # TEAMS_INFO{match_num, round_num, team_num, team_name, custom_ip}
    SCORES = "scores"
    # SCORES{time[seconds], penalty[seconds], score[seconds], stamp_time[seconds], start_time[seconds]}
    ROBOT_CONNECTION = "robot_connection"  # TODO: ask Matt why this function is commented out
    # CONNECTIONS{team_num: int, connected: bool}
    GAME_INFO = "game_info"
    # GAME_INFO{tinder, buttons activated}
    SENSORS_INFO = "sensors_info"
    # SENSORS_INFO{tinder}
    STAGE = "stage"
    # STAGE{is_auto[boolean], start_time[datetime]}
    BIOME = "biome"
    # BIOME{string}
    ALL_INFO = "all_info"
    # ALL_INFO{}


class SENSOR_HEADER():
    """
    Headers used for Shepherd to send messages to the Sensor Interface.
    """
    TURN_ON_LIGHT = "turn_on_light"
    # {num: int}
    TURN_OFF_LIGHT = "turn_off_light"
    # {num: int}
    SET_TRAFFIC_LIGHT = "set_traffic_light"
    SET_ALL_SENSORS = "set_all_sensors"
    TURN_ON_FIRE_LIGHT = "turn_on_fire_light"
    TURN_OFF_FIRE_LIGHT = "turn_off_fire_light"
    TURN_ON_LASERS = "turn_on_lasers"
    TURN_OFF_LASERS = "turn_off_lasers"
    TURN_OFF_TRAFFIC_LIGHT = "turn_off_traffic_light"

# pylint: disable=invalid-name


class SCOREBOARD_HEADER():
    """
    These are headers used by Shepherd to send information to the Scoreboard.
    """
    SCORES = "scores"
    # SCORES{time[seconds], penalty[seconds], score[seconds], stamp_time[seconds], start_time[seconds]}
    # overrides (send this at the very end)
    # time = elapsed time (count up) -> dummy time (DONT SEND) if dont update
    # penalty = positive time
    # stamps = negative time (decrement penalty) -> 5 for auto, 3 for tele
    # TODO:
    # account for penalty / stamp:
    #   display penalty / stamp
    #   update penalty / stamp time
    # time: change displayed time to this if not null(?)

    TEAM = "team"
    # TEAM{match_num, round_num, team_num, team_name, custom_ip}
    STAGE = "stage"
    # STAGE{stage, start_time}
    # start_time = timestamp
    # TODO:
    # stage: figure out stage to display mapping
    #   Autonomous vs Teleop
    # fix the boxes so there's a box for stage
    # reverse the timer: DONE
    # calculate the diff between the start_time and our current time (to account for delay): DONE
    # start the timer from the appropriate time: DONE
    RESET_TIMERS = "reset_timers"
    SANDSTORM = "sandstorm"
    # SANDSTORM{on[bool]}

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
    AUTO_TIME = 20  # 20
    TOTAL_TIME = 600 # 600
    STOPLIGHT_TIME = 30  # 30
    SANDSTORM_COVER_TIME = 10 # 10
    DEHYRATION_TIME = 30 # 30
    ROBOT_DEHYDRATED_TIME = 10 # 10
    SPREADSHEET_ID = "1moB8OJC3E8OwnXrRJmO-m5qn_ivXuZzsFse6-LdJy4I"
    CSV_FILE_NAME = "Sheets/sc2021.csv"
    STUDENT_DECODE_TIME = 1
    STOPLIGHT_PENALTY = 8

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
    # FOREST = "forest"
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
