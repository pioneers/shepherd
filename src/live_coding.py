"""
live_coding.py — One-shot loader for the live-coding challenge bank.

Parses live/q.csv (pipe-delimited: name | description | starter code | tests,
with "+-=" standing in for newlines inside cells) into four parallel lists,
then waits for shepherd.py to send PARSE_LIVE_FILE and replies with
SEND_LIVE_FILE_TO_SHEPHERD carrying the parsed lists. Shepherd caches them
and distributes challenges to the four station UIs via LIVE_HEADER.

Note: this process subscribes to the SHEPHERD YDL target (same mailbox as
shepherd.py and whack_a_mole.py) so it can see the PARSE_LIVE_FILE request,
and it exits after answering once.
"""
import csv
from ydl import Client
from utils import *


YC = Client(YDL_TARGETS.SHEPHERD)

LIVE_FILE_PATH = "./live/q.csv"
DELIMITER = '|'   # cells are pipe-separated so code can contain commas
CRLF = "+-="      # placeholder for newlines inside a CSV cell

def read():
    sheep_names = []
    sheep_descs = []
    sheep_bases = []
    sheep_tests = []

    #create an empty 2-D array
    #rows, cols = (0,0)
    #arr = [[0 for i in range(cols)] for j in range(rows)]

    #read from csv file
    with open(LIVE_FILE_PATH, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=DELIMITER)
        for row in spamreader:
            sheep_names.append(row[0])
            sheep_descs.append(row[1])
            sheep_bases.append(row[2])
            sheep_tests.append(row[3])


    #csv file is now in each for-loop

    #replace
    sheep_bases = [s.replace(CRLF, "\n") for s in sheep_bases]
    sheep_descs = [s.replace(CRLF, "\n") for s in sheep_descs]

    return sheep_names, sheep_descs, sheep_bases, sheep_tests



if __name__ == "__main__":
    while True:
        msg = YC.receive()
        if msg[1] == "parse_live_file":
            sheep_names, sheep_descs, sheep_bases, sheep_tests = read()
            YC.send(SHEPHERD_HEADER.SEND_LIVE_FILE_TO_SHEPHERD(
                sheep_names, sheep_descs, sheep_bases, sheep_tests))
            break
