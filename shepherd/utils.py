# pylint: disable=invalid-name
from ydl import header

class YDL_TARGETS():
    SHEPHERD = "ydl_target_shepherd"
    UI = "ydl_target_ui"
    SENSORS = "ydl_target_sensors"

class SHEPHERD_HEADER():
    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "button_press")
    def BUTTON_PRESS(id):
        """
        source: sensors. Notifies that a button has been pressed
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "turn_light_ui")
    def TURN_LIGHT_FROM_UI(num, type, on):
        """
        source: UI. Asks shepherd to turn a light on or off
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "get_match_info")
    def GET_MATCH_INFO():
        """
        source: UI. Asks Shepherd what match info is currently cached.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "set_match_number")
    def SET_MATCH_NUMBER(match_num):
        """
        source: UI. Sets the match number. Shepherd then fetches
        information for that match and sends it to the UI.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "set_teams_info")
    def SET_TEAMS_INFO(teams):
        """
        teams = 4*{team_name, team_num, robot_ip, [starting_position]}
        source: Sheet. Sets the match info, which has been fetched from a spreadsheet
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "send_scores")
    def SEND_SCORES(scores):
        """
        scores = [blue, gold]
        source: Sheet.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "setup_match")
    def SETUP_MATCH(match_num, teams):
        """
        sets up the match given all the match info
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "reset_match")
    def RESET_MATCH():
        """
        source: UI. Resets the match, moving back to setup.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "get_scores")
    def GET_SCORES():
        """
        source: UI. Asks Shepherd what the current scores are.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "set_scores")
    def SET_SCORES(blue_score=None, gold_score=None):
        """
        source: UI. adjusts the current scores to the input scores.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "get_state")
    def GET_STATE():
        """
        source: UI. Asks Shepherd what the current game state is.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "set_state")
    def SET_STATE(state):
        """
        source: UI. Sets the game state.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "start_next_stage")
    def START_NEXT_STAGE():
        """
        starts the next stage
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "reset_current_stage")
    def RESET_CURRENT_STAGE():
        """
        resets the current stage
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "stage_timer_end")
    def STAGE_TIMER_END():
        """
        source: Timer. Sent when a stage timer has ended.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "get_connection_status")
    def GET_CONNECTION_STATUS():
        """
        source: UI. Asks Shepherd to send robot connection statuses to UI.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "set_robot_ip")
    def SET_ROBOT_IP(ind, robot_ip):
        """
        source: UI. Attempts to connect team to robot with given ip.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "disconnect_robot")
    def DISCONNECT_ROBOT(ind):
        """
        source: UI. Takes in index and disconnects their robot.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "robot_off")
    def ROBOT_OFF(ind):
        """
        source: UI. Takes in index and disables their robot.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "robot_on")
    def ROBOT_ON(ind):
        """
        source: UI. Takes in index and enables their robot.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "sound_blizzard_warning")
    def SOUND_BLIZZARD_WARNING():
        """
        source: Timer. Plays the blizzard warning sound.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "pause_timer")
    def PAUSE_TIMER():
        """
        source: UI. Pauses GAME_TIMER in Shepherd; used in the event that the game
        needs to be paused and continued from the state it was paused at.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "resume_timer")
    def RESUME_TIMER():
        """
        source: UI. Resume GAME_TIMER in Shepherd; used to resume the game after it has
        been paused using PAUSE_TIMERS.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "start_whackamole")
    def START_WHACKAMOLE():
        """
        Starts a new game of whackamole
        """
    



class UI_HEADER():
    """
    These are headers used by Shepherd to send information to the Staff UI.
    """
    @staticmethod
    @header(YDL_TARGETS.UI, "all_info")
    def ALL_INFO():
        """
        used for match recovery
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "teams_info")
    def TEAMS_INFO(match_num, teams):
        """
        info about teams
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "scores")
    def SCORES(blue_score: int, gold_score: int):
        """
        score for each alliance
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "robot_connection")
    def ROBOT_CONNECTION(ind: int, connected: bool, robot_ip: str):
        """
        source: runtimeclient. robot connection
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "runtime_status")
    def RUNTIME_STATUS(ind: int, shep_connected: bool, dawn_connected: bool, \
        mode, battery: float, version: str):
        """
        source: runtimeclient. runtime status
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "state")
    def STATE(state, start_time=None, state_time=None):
        """
        tells UI that Shepherd is now in this state
        TODO: is this redundant with teams_info?
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "reset_timers")
    def RESET_TIMERS():
        """
        reset all timers. (not used anymore)
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "pause_timer")
    def PAUSE_TIMER():
        """
        source: Shepherd. Pauses the game timer in scoreboard by clearing the timeout created in runStageTimer;
        Used in the event that the game
        needs to be paused and continued from the state it was paused at.
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "resume_timer")
    def RESUME_TIMER(end_time, pause_end):
        """
        source: Shepherd. Resumes the game timer in scoreboard by setting a new timeout
        Used to resume the game after it has
        been paused using PAUSE_TIMERS.
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "scores_for_icons")
    def SCORES_FOR_ICONS(blue_score, gold_score):
        """
        source: Sheet. Used to update the number score per team as well as 
        update the icons such as the pioneers/campsites on the scoreboard UI
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "invalid_write_match")
    def INVALID_WRITE_MATCH(match_num, reason=0):
        """
        source: Sheet. Used to send an alert message to UI saying why
        the request to write to the spreadsheet was invalid.
        If reason=1, we don't allow negative numbers because reading/writing -1 from
        google sheets gives us a str instead of an int which complicates code
        """
    
    @staticmethod
    @header(YDL_TARGETS.UI, "update_player_score")
    def UPDATE_PLAYER_SCORE(score):
        """
        Updates and displays the current player's whackamole score
        on whackamole.html. This should update every instance a 
        light is turned on. 
        """
    
    @staticmethod
    @header(YDL_TARGETS.UI, "game_over")
    def GAME_OVER():
        """
        Tells user that they have lost in the game of whackamole. 
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

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "turn_on_button_light")
    def TURN_ON_BUTTON_LIGHT(id: int):
      """
      example header doc string
      """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "turn_off_button_light")
    def TURN_OFF_BUTTON_LIGHT(id: int):
      """
      example header doc string
      """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "turn_on_midline")
    def TURN_ON_MIDLINE(id: int):
      """
      example header doc string
      """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "turn_off_midline")
    def TURN_OFF_MIDLINE(id: int):
      """
      example header doc string
      """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "turn_on_lasers")
    def TURN_ON_LASERS():
      """
      example header doc string
      """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "turn_off_lasers")
    def TURN_OFF_LASERS():
      """
      example header doc string
      """


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
    "whackamole.html": False,
}



class CONSTANTS():
    BLIZZARD_WARNING_TIME = 170
    CSV_FILE_NAME = "sheets/Shepherd Evergreen Database - Match Database.csv"
    SPREADSHEET_ID = "11pJgMl_AXHWyu3QFoM6Rc_-5GkNmOx1UR0HYF1o8KwI"
    UI_PASSWORD_HASH = "44590c963be2a79f52c07f7a7572b3907bf5bb180d993bd31aab510d29bbfbd3"


class ALLIANCE_COLOR():
    GOLD = "gold"
    BLUE = "blue"


class INDICES():
    BLUE_1 = 0
    BLUE_2 = 1
    GOLD_1 = 2
    GOLD_2 = 3


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
    STATE.TELEOP_1: 180,
    STATE.BLIZZARD: 15,
    STATE.TELEOP_2: 45,
    STATE.ENDGAME: 60
}

class PROTOBUF_TYPES():
    RUN_MODE = 0
    START_POS = 1
    LOG = 2  # text proto
    DEVICE_DATA = 3
    GAME_STATE = 4
