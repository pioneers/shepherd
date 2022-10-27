"""YDL: interprocess communication over TCP sockets

Import the ydl module to initialize a YDL client or server:

Process 0:
    >>> from ydl import run_ydl_server
    >>> run_ydl_server()

Process 1:
    >>> from ydl import YDLClient
    >>> yc = YDLClient()
    >>> yc.send(("process 2", "stuff"))

Process 2:
    >>> from ydl import YDLClient
    >>> yc = YDLClient("process 2")
    >>> yc.receive()
    ('process 2', 'stuff')
"""

from ._core import DEFAULT_YDL_ADDR, YDLClient, run_ydl_server
from ._header import header