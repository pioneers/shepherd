# pylint: disable=invalid-name
from ydl import Handler, header


class YDL_TARGETS():
    SHEPHERD = "ydl_target_shepherd"
    UI = "ydl_target_ui"
    SENSORS = "ydl_target_sensors"
    LIVE = "ydl_target_challenges"


class SHEPHERD_HEADER():
    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "button_press")
    def BUTTON_PRESS(id):
        """
        source: sensors. Notifies that a button has been pressed
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "turn_on_button_light")
    def TURN_ON_BUTTON_LIGHT(id: int):
        """
        Digital Write: HIGH
        """

    @staticmethod
    @header(YDL_TARGETS.SHEPHERD, "turn_off_button_light")
    def TURN_OFF_BUTTON_LIGHT(id: int):
        """
        Digital Write: LOW
        """


# A dictionary of pages -> whether page is password protected
# password.html should not be included in this list, since
# server.py will just route to that automatically
# add additional pages here

UI_PAGES = {
    "whackamole.html": True,
}


class STATE():
    SETUP = "setup"
    AUTO = "auto"
    TELEOP_1 = "teleop_1"
    END = "end"


class SHEPHERD_HANDLER():
    EVERYWHERE = Handler()
    SETUP = Handler()
    AUTO = Handler()
    TELEOP_1 = Handler()
    END = Handler()


STATE_HANDLERS = {
    STATE.SETUP: SHEPHERD_HANDLER.SETUP,
    STATE.AUTO: SHEPHERD_HANDLER.AUTO,
    STATE.TELEOP_1: SHEPHERD_HANDLER.TELEOP_1,
    STATE.END: SHEPHERD_HANDLER.END
}


class PROTOBUF_TYPES():
    RUN_MODE = 0
    START_POS = 1
    LOG = 2  # text proto
    DEVICE_DATA = 3
    GAME_STATE = 2
