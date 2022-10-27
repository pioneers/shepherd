"""
Run a YDL server, which clients can use to communicate.
"""

import argparse
import signal
import sys
from ._core import run_ydl_server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='python3 -m ydl', description=__doc__)
    parser.add_argument("-s", "--silent", action='store_true',
        help="do not print client connections")
    parser.add_argument("-a", "--address", default=None, type=str,
        help="run server on specified ip address, such as 0.0.0.0")
    parser.add_argument("-p", "--port", default=None, type=int,
        help="run server on specified port")

    args = parser.parse_args()
    verbose = not args.silent
    def sigint_handler(_signum, _frame):
        '''gracefully shuts down server on sigint (ctrl-c)'''
        if verbose:
            print("\nShutting down YDL server")
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)
    run_ydl_server(args.address, args.port, verbose)
