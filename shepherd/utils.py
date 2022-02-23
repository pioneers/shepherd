# pylint: disable=invalid-name
from header import header

class YDL_TARGETS():
    SHEPHERD = "ydl_target_shepherd"
    UI = "ydl_target_ui"
    SENSORS = "ydl_target_sensors"

class SHEPHERD_HEADER():
    @header(YDL_TARGETS.SHEPHERD, "get_match_info")
    def GET_MATCH_INFO():
        """
        source: UI. Asks Shepherd what match info is currently cached.
        """

    @header(YDL_TARGETS.SHEPHERD, "set_match_number")
    def SET_MATCH_NUMBER(match_num):
        """
        source: UI. Sets the match number. Shepherd then fetches
        information for that match and sends it to the UI.
        """

    @header(YDL_TARGETS.SHEPHERD, "set_teams_info")
    def SET_TEAMS_INFO(teams):
        """
        teams = 4*{team_name, team_num, robot_ip, [starting_position]}
        source: Sheet. Sets the match info, which has been fetched from a spreadsheet
        """

    @header(YDL_TARGETS.SHEPHERD, "setup_match")
    def SETUP_MATCH(match_num, teams):
        """
        sets up the match given all the match info
        """

    @header(YDL_TARGETS.SHEPHERD, "reset_match")
    def RESET_MATCH():
        """
        source: UI. Resets the match, moving back to setup.
        """

    @header(YDL_TARGETS.SHEPHERD, "get_scores")
    def GET_SCORES():
        """
        source: UI. Asks Shepherd what the current scores are.
        """

    @header(YDL_TARGETS.SHEPHERD, "set_scores")
    def SET_SCORES(blue_score=None, gold_score=None):
        """
        source: UI. adjusts the current scores to the input scores.
        """

    @header(YDL_TARGETS.SHEPHERD, "get_state")
    def GET_STATE():
        """
        source: UI. Asks Shepherd what the current game state is.
        """

    @header(YDL_TARGETS.SHEPHERD, "set_state")
    def SET_STATE(state):
        """
        source: UI. Sets the game state.
        """

    @header(YDL_TARGETS.SHEPHERD, "start_next_stage")
    def START_NEXT_STAGE():
        """
        starts the next stage
        """

    @header(YDL_TARGETS.SHEPHERD, "reset_current_stage")
    def RESET_CURRENT_STAGE():
        """
        resets the current stage
        """

    @header(YDL_TARGETS.SHEPHERD, "stage_timer_end")
    def STAGE_TIMER_END():
        """
        source: Timer. Sent when a stage timer has ended.
        """

    @header(YDL_TARGETS.SHEPHERD, "get_connection_status")
    def GET_CONNECTION_STATUS():
        """
        source: UI. Asks Shepherd to send robot connection statuses to UI.
        """

    @header(YDL_TARGETS.SHEPHERD, "set_robot_ip")
    def SET_ROBOT_IP(ind, robot_ip):
        """
        source: UI. Attempts to connect team to robot with given ip.
        """

    @header(YDL_TARGETS.SHEPHERD, "robot_off")
    def ROBOT_OFF(ind):
        """
        source: UI. Takes in index and disables their robot.
        """

    @header(YDL_TARGETS.SHEPHERD, "robot_on")
    def ROBOT_ON(ind):
        """
        source: UI. Takes in index and enables their robot.
        """

    @header(YDL_TARGETS.SHEPHERD, "sound_blizzard_warning")
    def SOUND_BLIZZARD_WARNING():
        """
        source: Timer. Plays the blizzard warning sound.
        """

class UI_HEADER():
    """
    These are headers used by Shepherd to send information to the Staff UI.
    """
    @header(YDL_TARGETS.UI, "all_info")
    def ALL_INFO():
        """
        used for match recovery
        """

    @header(YDL_TARGETS.UI, "teams_info")
    def TEAMS_INFO(match_num, teams):
        """
        info about teams
        """

    @header(YDL_TARGETS.UI, "scores")
    def SCORES(blue_score: int, gold_score: int):
        """
        score for each alliance
        """

    @header(YDL_TARGETS.UI, "robot_connection")
    def ROBOT_CONNECTION(ind: int, connected: bool, robot_ip: str):
        """
        source: runtimeclient. robot connection
        """

    @header(YDL_TARGETS.UI, "runtime_status")
    def RUNTIME_STATUS(ind: int, shep_connected: bool, dawn_connected: bool, \
        mode, battery: float, version: str):
        """
        source: runtimeclient. runtime status
        """

    @header(YDL_TARGETS.UI, "state")
    def STATE(state, start_time=None, state_time=None):
        """
        tells UI that Shepherd is now in this state
        TODO: is this redundant with teams_info?
        """
    @header(YDL_TARGETS.UI, "reset_timers")
    def RESET_TIMERS():
        """
        reset all timers
        """


class SENSOR_HEADER():
    """
    Headers used for Shepherd to send messages to the Sensor Interface.
    """
    # @header(YDL_TARGETS.SENSORS, "example_header")
    # def EXAMPLE_HEADER():
    #   """
    #   example header doc string
    #   """

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
    BLIZZARD_WARNING_TIME = 20
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
    MATCH = {
        "TYPE": "match", 
        "FUNCTION": SHEPHERD_HEADER.STAGE_TIMER_END.name
    }
    BLIZZARD_WARNING = {
        "TYPE": "yolo",
        "FUNCTION": SHEPHERD_HEADER.SOUND_BLIZZARD_WARNING.name
    }


class STATE():
    SETUP = "setup"
    AUTO = "auto"
    TELEOP_1 = "teleop_1"
    BLIZZARD = "blizzard"
    TELEOP_2 = "teleop_2"
    ENDGAME = "endgame"
    END = "end"

STAGE_TIMES = {
    STATE.AUTO: 30,
    STATE.TELEOP_1: 30,
    STATE.BLIZZARD: 15,
    STATE.TELEOP_2: 75,
    STATE.ENDGAME: 30

    # STATE.AUTO: 3,
    # STATE.TELEOP_1: 3,
    # STATE.BLIZZARD: 15,
    # STATE.TELEOP_2: 3,
    # STATE.ENDGAME: 3
}

class PROTOBUF_TYPES():
    RUN_MODE = 0
    START_POS = 1
    LOG = 2  # text proto
    DEVICE_DATA = 3
    GAME_STATE = 4
