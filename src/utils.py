# pylint: disable=invalid-name
"""
utils.py — The shared "protocol definition" for the whole system.

Every process imports this file. It defines:
  * YDL_TARGETS   — the named mailboxes on the YDL message bus.
  * *_HEADER      — every message type in the system, grouped by recipient
                    (SHEPHERD_HEADER = messages TO shepherd.py, UI_HEADER =
                    messages TO the browser UIs via server.py, etc.). Each
                    header is a function decorated with @header(target, name);
                    calling it, e.g. SHEPHERD_HEADER.SET_STATE(state="auto"),
                    returns the (target, name, args) tuple that YC.send() takes.
                    The docstrings on each header double as protocol docs —
                    "source:" says which process sends it.
  * UI_PAGES      — which HTML pages server.py serves and which need a password.
  * CONSTANTS / enums (STATE, ALLIANCE_COLOR, INDICES) shared by everyone.
  * SHEPHERD_HANDLER / STATE_HANDLERS / STAGE_TIMES — the scaffolding for
    shepherd.py's per-state event dispatch and stage durations.

If you add a new message anywhere in the system, it gets defined here first.
"""
from ydl import Handler, header


class YDL_TARGETS():
    """Named recipients on the YDL bus. Each process subscribes to one."""
    SHEPHERD = "ydl_target_shepherd"      # shepherd.py (+ whack_a_mole, live_coding)
    UI = "ydl_target_ui"                  # server.py, which relays to browsers
    SENSORS = "ydl_target_sensors"        # sensors_config.py (field hardware)
    LIVE = "ydl_target_challenges"        # live coding challenge stations


class SHEPHERD_HEADER():
    """
    Messages addressed TO shepherd.py. Senders include the UI (via server.py),
    the sensor process, the Sheet background threads, the timer callback,
    whack_a_mole.py, and live_coding.py.
    """
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
    @header(YDL_TARGETS.SHEPHERD, "update_alliance_selection")
    def UPDATE_ALLIANCE_SELECTION(alliances):
        """
        alliances: A list of lists, where each list is the length of
        an alliance and contains the name of each school. Updates the
        Google Sheets with the alliances selected.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "update_security_breach_score")
    def UPDATE_SECURITY_BREACH_SCORE(alliance, done):
        """
        alliance: 'blue' or 'gold'
        source: whack_a_mole.py update the security breach score for the alliance.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "update_cheat_code_score")
    def UPDATE_CHEAT_CODE_SCORE(alliance, score):
        """
        alliance: 'blue' or 'gold'
        source: whack_a_mole.py update the cheat code score for the alliance.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "set_cheat_code")
    def SET_CHEAT_CODE(alliance, CHEAT_CODE):
        """
        alliance: 'blue' or 'gold'
        source: whack_a_mole.py send the cheat code information for the alliance.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "send_challenges_state")
    def SEND_CHALLENGES_STATE(state):
        pass
    
    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "send_challenges_score")
    def SEND_CHALLENGES_SCORE(team, score):
        """
        team: 0, 1, 2, or 3. Check enum INDICES.
        score: live coding score.
        source: LIVE.
        """
    
    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "live_four_sheep_state")
    def LIVE_FOUR_SHEEP_STATE(team, fetched):
        """
        team: 0, 1, 2, or 3. Check enum INDICES.
        fetched: whether or not the team has live challenges correctly configured
        source: LIVE.
        """
    
    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "parse_live_file")
    def PARSE_LIVE_FILE():
        """
        signal live_coding.py to parse csv
        source: SHEPHERD.
        """
    
    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "send_live_file_to_shepherd")
    def SEND_LIVE_FILE_TO_SHEPHERD(sheep_names, sheep_descs, sheep_bases, sheep_tests):
        """
        send parsed csv from live_coding.py to shepherd.py
        source: LIVE_CODING.
        """
    
    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "start_whackamole")
    def START_WHACKAMOLE():
        """
        ***Whack-A-Mole***
        Starts a new game of whackamole. For Demo Purpose only.
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "send_sail_status")
    def SEND_SAIL_STATUS(alliance):
        """
        Writes sail confirmation when alliance completes whack a mole
        challenge into sheet for Spring 2025.
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
    def RUNTIME_STATUS(ind: int, shep_connected: bool, dawn_connected: bool,
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
    @header(YDL_TARGETS.UI, "play_start_sound")
    def PLAY_START_SOUND():
        """
        source: Shepherd. Plays the start sound when the game starts
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "play_end_sound")
    def PLAY_END_SOUND():
        """
        source: Shepherd. Plays the end sound when the game ends
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "set_cheat_code")
    def SET_CHEAT_CODE(blue_cheat_code, gold_cheat_code):
        """
        source: Shepherd. Send ceat code infomation to UI
        """

    @staticmethod
    @header(YDL_TARGETS.UI, "update_player_score")
    def UPDATE_PLAYER_SCORE(score):
        """
        ***Whack-A-Mole***
        Updates and displays the current player's whackamole score
        on whackamole.html. This should update every instance a 
        light is turned on. 
        """
    
    @staticmethod
    @header(YDL_TARGETS.UI, "whack_a_mole_game_over")
    def WHACK_A_MOLE_GAME_OVER():
        """
        ***Whack-A-Mole***
        Tells user that they have lost in the game of whackamole. 
        """


class LIVE_HEADER():
    """
    Messages addressed TO the live-coding challenge stations ("bleatcode"
    UIs) — the per-team laptops where students solve coding challenges
    mid-match for points.
    """
    @staticmethod
    @header(YDL_TARGETS.LIVE, "set_challenge")
    def SET_CHALLENGE(challenges, codes):
        """
        source: Shepherd
        Sends list of coding challenges and cheat codes (disabled in year Haiku) 
        to live coding challenges UI.
        """
    
    @staticmethod
    @header(YDL_TARGETS.LIVE, "set_live_challenges")
    def SET_LIVE_CHALLENGES(team, sheep_names, sheep_descs, sheep_bases, sheep_tests):
        """
        send parsed csv from shepherd.py to main.js in bleatcode
        team: 0, 1, 2, or 3. Check enum INDICES.
        source: SHEPHERD.
        """
        
    @staticmethod
    @header(YDL_TARGETS.LIVE, "pause_timer")
    def PAUSE_TIMER():
        """
        source: Shepherd. Pauses the game timer in scoreboard by clearing the timeout created in runStageTimer;
        Used in the event that the game
        needs to be paused and continued from the state it was paused at.
        """

    @staticmethod
    @header(YDL_TARGETS.LIVE, "resume_timer")
    def RESUME_TIMER(end_time, pause_end):
        """
        source: Shepherd. Resumes the game timer in scoreboard by setting a new timeout
        Used to resume the game after it has
        been paused using PAUSE_TIMERS.
        """

    @staticmethod
    @header(YDL_TARGETS.LIVE, "state")
    def STATE(state, start_time=None, state_time=None):
        """
        tells UI that Shepherd is now in this state
        """

    @staticmethod
    @header(YDL_TARGETS.LIVE, "reset_base_challenges")
    def RESET_BASE_CHALLENGES():
        pass
    
    @staticmethod
    @header(YDL_TARGETS.LIVE, "default_code_base")
    def DEFAULT_CODE_BASE():
        """
        source: Shepherd. Tells live challenges UIs to display the default code
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
        Digital Write: HIGH
        """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "turn_off_button_light")
    def TURN_OFF_BUTTON_LIGHT(id: int):
        """
        Digital Write: LOW
        """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "lower_sail")
    def LOWER_SAIL(alliance: str):
        """
        Digital Write LOW followed by HIGH
        """

    @staticmethod
    @header(YDL_TARGETS.SENSORS, "raise_sail")
    def RAISE_SAIL(alliance: str):
        """
        Digital Write LOW followed by HIGH (opposite)
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
    "match_creator.html": True,
    "alliance_selection.html": True,
    "bracket_ui.html": False,
    "whackamole.html": True,
}


class CONSTANTS():
    BLIZZARD_WARNING_TIME = 170
    # Offline fallback for match schedules when Google Sheets is unreachable
    CSV_FILE_NAME = "sheets/Shepherd Evergreen Database - Match Database.csv"
    # The Google Sheet used as the season's match/score database
    SPREADSHEET_ID = "1JO1vo0cUzIvIk2QfgL9e4c7ltMw4OwTcK0Wlk75P-iI"
    # sha256(password + "cheese"); checked by server.py for staff pages
    UI_PASSWORD_HASH = "44590c963be2a79f52c07f7a7572b3907bf5bb180d993bd31aab510d29bbfbd3"


class ALLIANCE_COLOR():
    GOLD = "gold"
    BLUE = "blue"


class INDICES():
    """Canonical ordering of the 4 robots, used for teams lists,
    CLIENTS (runtime connections), and live-coding station numbers."""
    BLUE_1 = 0
    BLUE_2 = 1
    GOLD_1 = 2
    GOLD_2 = 3


class STATE():
    """The stages of a match, in order. shepherd.py holds exactly one of
    these at a time and it gates which handlers run."""
    SETUP = "setup"        # teams loaded, waiting for match start
    AUTO = "auto"          # autonomous period (robots run their own code)
    TELEOP_1 = "teleop_1"  # driver-controlled period
    END = "end"            # match over; scores flushed


class SHEPHERD_HANDLER():
    """One event-handler registry per state, plus EVERYWHERE for handlers
    that should fire regardless of state. shepherd.py's functions register
    themselves into these via decorators."""
    EVERYWHERE = Handler()
    SETUP = Handler()
    AUTO = Handler()
    TELEOP_1 = Handler()
    END = Handler()


# Which handler group shepherd.py consults for each game state.
STATE_HANDLERS = {
    STATE.SETUP: SHEPHERD_HANDLER.SETUP,
    STATE.AUTO: SHEPHERD_HANDLER.AUTO,
    STATE.TELEOP_1: SHEPHERD_HANDLER.TELEOP_1,
    STATE.END: SHEPHERD_HANDLER.END
}

# Duration of each timed stage, in seconds (SETUP/END are untimed).
STAGE_TIMES = {
    STATE.AUTO: 20,
    STATE.TELEOP_1: 270,
}


class PROTOBUF_TYPES():
    """Message-type bytes prefixed to protobufs on the Shepherd<->Runtime
    TCP socket (see runtimeclient.py). Must match Runtime's expectations."""
    RUN_MODE = 0
    START_POS = 1
    LOG = 2  # text proto
    DEVICE_DATA = 3
    GAME_STATE = 2
