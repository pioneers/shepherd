from ydl import Client
from utils import *


###########################################
# Evergreen Variables
###########################################
YC = Client(YDL_TARGETS.SHEPHERD)
MATCH_NUMBER: int = -1
GAME_STATE: str = STATE.END


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
        SHEPHERD_HANDLER.EVERYWHERE.handle(payload)

        if GAME_STATE in STATE_HANDLERS:
            handler = STATE_HANDLERS.get(GAME_STATE)
            handler.handle(payload)
        else:
            print(f"Invalid State: {GAME_STATE}")


###########################################
# Event to Function Mappings for each Stage
###########################################
# pylint: disable=no-member
if __name__ == '__main__':
    start()
