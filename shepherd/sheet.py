# installation:
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# source: https://developers.google.com/sheets/api/quickstart/python

import os
import csv
import threading
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from ydl import YDLClient
from utils import *

# If modifying these scopes, delete your previously saved credentials
# at USER_TOKEN_FILE
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRET_FILE = 'sheets/client_secret.json'
USER_TOKEN_FILE = "sheets/user_token.json" # user token; do not upload to github (.gitignore it)
YC = YDLClient()

"""
Sheet structure: [match #, blue 1 #, blue 1 name, blue 1 ip, blue 2 #, ...]
"""

class Sheet:
    @staticmethod
    def get_match(match_number):
        '''
        Given a match number, gets match info and sends it back to Shepherd through ydl.
        First attempts to use online spreadsheet, and falls back to csv file if offline
        '''
        def bg_thread_work():
            game_data = [[]]
            try:
                spreadsheet = Sheet.__get_authorized_sheet()
                game_data = spreadsheet.values().get(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
                    range="Match Database!A2:M").execute()['values']
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Fetching data from offline csv file")
                with open(CONSTANTS.CSV_FILE_NAME) as csv_file:
                    game_data = list(csv.reader(csv_file, delimiter=','))[1:]

            return_len = 13
            lst = [""] * return_len
            for row in game_data:
                if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                    lst = row[1:return_len+1] + [""]*(return_len+1-len(row))
                    break
            teams = [{},{},{},{}]
            for a in range(4):
                teams[a]["team_num"] = int(lst[3*a]) if lst[3*a].isdigit() else -1
                teams[a]["team_name"] = lst[3*a+1]
                teams[a]["robot_ip"] = lst[3*a+2]
            YC.send(SHEPHERD_HEADER.SET_TEAMS_INFO(teams=teams))

        threading.Thread(target=bg_thread_work).start()

    @staticmethod
    def read_scores(match_number):
        def bg_thread_work():
            try:
                Sheet.__read_online_scores(match_number)
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Unable to read from spreadsheet")
        threading.Thread(target=bg_thread_work).start()

    @staticmethod
    def write_scores(match_number, blue_score, gold_score):
        def bg_thread_work():
            try:
                Sheet.__write_online_scores(match_number, blue_score, gold_score)
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Unable to write to spreadsheet")
        threading.Thread(target=bg_thread_work).start()
    
    @staticmethod
    def write_scores_from_read_scores(match_number):
        def bg_thread_work():
            try:
                Sheet.__write_scores_from_read_scores(match_number)
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Unable to read & write to spreadsheet")
        threading.Thread(target=bg_thread_work).start()
    
    @staticmethod
    def send_scores_for_icons(match_number):
        def bg_thread_work():
            try:
                Sheet.__send_online_scores_for_icons(match_number)
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Unable to send score from spreadsheet")
        threading.Thread(target=bg_thread_work).start()
    
    @staticmethod
    def write_match_info(match_number, teams):
        def bg_thread_work():
            try:
                Sheet.__write_match_info(match_number, teams)
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Unable to write match info to spreadsheet")
        threading.Thread(target=bg_thread_work).start()

    @staticmethod
    def __get_authorized_sheet():
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        returns a google spreadsheet service thingy
        """
        creds = None
        if os.path.exists(USER_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(USER_TOKEN_FILE, 'w') as token:
                    print(f"Storing google auth credentials to {USER_TOKEN_FILE}")
                    token.write(creds.to_json())
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets() # pylint: disable=no-member

    @staticmethod
    def __read_online_scores(match_number):
        """
        Sends (blue score, gold score)
        """
        spreadsheet = Sheet.__get_authorized_sheet()
        game_data = spreadsheet.values().get(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range="Ref Scoring!A4:C").execute()['values']

        blue = None
        gold = None
        for _, row in enumerate(game_data):
            if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                if row[1] == "Blue":
                    blue = row[2]
                    if blue is not None and gold is not None:
                        YC.send(SHEPHERD_HEADER.SET_SCORES(blue_score=blue, gold_score=gold))
                        return blue, gold
                elif row[1] == "Gold":
                    gold = row[2]
                    if blue is not None and gold is not None:
                        YC.send(SHEPHERD_HEADER.SET_SCORES(blue_score=blue, gold_score=gold))
                        return blue, gold

    @staticmethod
    def __write_online_scores(match_number, blue_score, gold_score):
        """
        A method that writes the scores to the sheet
        """
        spreadsheet = Sheet.__get_authorized_sheet()
        game_data = spreadsheet.values().get(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range="Match Database!A2:A").execute()['values']

        row_num = -1 # if this fails, it'll overwrite the header which is fine
        for i, row in enumerate(game_data):
            if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                row_num = i
                break

        range_name = f"Match Database!N{row_num + 2}:O{row_num + 2}"
        body = {
            'values': [[str(blue_score), str(gold_score)]]
        }
        spreadsheet.values().update(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range=range_name, body=body, valueInputOption="RAW").execute()
    
    @staticmethod
    def __write_scores_from_read_scores(match_number):
        """
        A method that writes the scores to the spreadsheet using scores from the spreadsheet
        (transfering scores from one spreadsheet tab to another)
        """
        scores = Sheet.__read_online_scores(match_number)
        if (scores == None):
            return
        blue_score, gold_score = scores[0], scores[1]

        spreadsheet = Sheet.__get_authorized_sheet()
        game_data = spreadsheet.values().get(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range="Match Database!A2:A").execute()['values']

        row_num = -1 # if this fails, it'll overwrite the header which is fine
        for i, row in enumerate(game_data):
            if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                row_num = i
                break

        range_name = f"Match Database!N{row_num + 2}:O{row_num + 2}"
        body = {
            'values': [[str(blue_score), str(gold_score)]]
        }
        spreadsheet.values().update(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range=range_name, body=body, valueInputOption="RAW").execute()

    @staticmethod
    def __send_online_scores_for_icons(match_number):
        """
        Sends all types of scores to ui
        """
        spreadsheet = Sheet.__get_authorized_sheet()
        game_data = spreadsheet.values().get(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range="Ref Scoring!A4:BL").execute()['values']
        
        blue = None
        gold = None
        for _, row in enumerate(game_data):
            if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                if row[1] == "Blue":
                    blue = {
                        "score" : int(row[2]),
                        "campsite-resource-top-left-leftside" : 0 if row[10] == "" else int(row[10]),
                        "campsite-resource-bottom-left-leftside" : 0 if row[12] == "" else int(row[12]),
                        "campsite-resource-top-middle-leftside" : 0 if row[14] == "" else int(row[14]),
                        "campsite-resource-bottom-middle-leftside" : 0 if row[16] == "" else int(row[16]),
                        "campsite-resource-top-right-leftside" : 0 if row[18] == "" else int(row[18]),
                        "campsite-resource-bottom-right-leftside" : 0 if row[20] == "" else int(row[20]),
                        "campsite-satellite-top-left" : (row[26] == "TRUE" or row[27] == "TRUE"),
                        "campsite-satellite-bottom-left" : (row[30] == "TRUE" or row[31] == "TRUE"),
                        "campsite-satellite-top-middle" : (row[34] == "TRUE" or row[35] == "TRUE"),
                        "campsite-satellite-bottom-middle" : (row[38] == "TRUE" or row[39] == "TRUE"),
                        "campsite-satellite-top-right" : (row[42] == "TRUE" or row[43] == "TRUE"),
                        "campsite-satellite-bottom-right" : (row[46] == "TRUE" or row[47] == "TRUE"),
                        "campsite-pioneer-top-left" : row[28] == "TRUE",
                        "campsite-pioneer-bottom-left" : row[32] == "TRUE",
                        "campsite-pioneer-top-middle" : row[36] == "TRUE",
                        "campsite-pioneer-bottom-middle" : row[40] == "TRUE",
                        "campsite-pioneer-top-right" : row[44] == "TRUE",
                        "campsite-pioneer-bottom-right" : row[48] == "TRUE",
                        "endgame-pioneer-blue" : int(0 if (row[57] == "") else 1) + int(0 if (row[58] == "") else 1)
                    }
                    if blue is not None and gold is not None:
                        YC.send(UI_HEADER.SCORES_FOR_ICONS(blue_score=blue, gold_score=gold))
                        return
                elif row[1] == "Gold":
                    gold = {
                        "score" : int(row[2]),
                        "campsite-resource-top-left-rightside" : 0 if row[10] == "" else int(row[10]),
                        "campsite-resource-bottom-left-rightside" : 0 if row[12] == "" else int(row[12]),
                        "campsite-resource-top-middle-rightside" : 0 if row[14] == "" else int(row[14]),
                        "campsite-resource-bottom-middle-rightside" : 0 if row[16] == "" else int(row[16]),
                        "campsite-resource-top-right-rightside" : 0 if row[18] == "" else int(row[18]),
                        "campsite-resource-bottom-right-rightside" : 0 if row[20] == "" else int(row[20]),
                        "campsite-satellite-top-left" : (row[26] == "TRUE" or row[27] == "TRUE"),
                        "campsite-satellite-bottom-left" : (row[30] == "TRUE" or row[31] == "TRUE"),
                        "campsite-satellite-top-middle" : (row[34] == "TRUE" or row[35] == "TRUE"),
                        "campsite-satellite-bottom-middle" : (row[38] == "TRUE" or row[39] == "TRUE"),
                        "campsite-satellite-top-right" : (row[42] == "TRUE" or row[43] == "TRUE"),
                        "campsite-satellite-bottom-right" : (row[46] == "TRUE" or row[47] == "TRUE"),
                        "campsite-pioneer-top-left" : row[28] == "TRUE",
                        "campsite-pioneer-bottom-left" : row[32] == "TRUE",
                        "campsite-pioneer-top-middle" : row[36] == "TRUE",
                        "campsite-pioneer-bottom-middle" : row[40] == "TRUE",
                        "campsite-pioneer-top-right" : row[44] == "TRUE",
                        "campsite-pioneer-bottom-right" : row[48] == "TRUE",
                        "endgame-pioneer-gold" : int(0 if (row[57] == "") else 1) + int(0 if (row[58] == "") else 1)
                    }
                    if blue is not None and gold is not None:
                        YC.send(UI_HEADER.SCORES_FOR_ICONS(blue_score=blue, gold_score=gold))
                        return


    @staticmethod
    def __write_match_info(match_number, teams):
        """
        Writes the match info to the spreadsheet
        """
        if (match_number < 0):
            YC.send(UI_HEADER.INVALID_WRITE_MATCH(match_num=match_number, reason=1))
            return False
        for i in range(len(teams)):
            if teams[i]["team_num"] < 0:
                YC.send(UI_HEADER.INVALID_WRITE_MATCH(match_num=match_number, reason=2))
                return False
        

        spreadsheet = Sheet.__get_authorized_sheet()
        game_data = spreadsheet.values().get(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range="Match Database!A2:A").execute()['values']
        row_num = -1
        for i, row in enumerate(game_data):
            row_num = i
            if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                YC.send(UI_HEADER.INVALID_WRITE_MATCH(match_num=match_number, reason=0))
                return False
        range_name = f"Match Database!A{row_num + 3}:M{row_num + 3}"
        body = {
            'values': [[match_number, teams[0]["team_num"], teams[0]["team_name"], teams[0]["robot_ip"],
                        teams[1]["team_num"], teams[1]["team_name"], teams[1]["robot_ip"],
                        teams[2]["team_num"], teams[2]["team_name"], teams[2]["robot_ip"],
                        teams[3]["team_num"], teams[3]["team_name"], teams[3]["robot_ip"]]]
        }
        spreadsheet.values().update(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range=range_name, body=body, valueInputOption="RAW").execute()
        

        spreadsheet = Sheet.__get_authorized_sheet()
        game_data = spreadsheet.values().get(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
            range="Ref Scoring!A4:B").execute()['values']
        row_num = -1
        blue = False
        gold = False
        empty_cell_blue = -1
        empty_cell_gold = -1
        for i, row in enumerate(game_data):
            row_num = i
            if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                if row[1] == "Blue":
                    blue = True
                    YC.send(UI_HEADER.INVALID_WRITE_MATCH(match_num=match_number, reason=3))
                    if blue is True and gold is True:
                        return
                elif row[1] == "Gold":
                    gold = True
                    YC.send(UI_HEADER.INVALID_WRITE_MATCH(match_num=match_number, reason=3))
                    if blue is True and gold is True:
                        return
            elif len(row) > 0 and row[0] == "":
                if (empty_cell_blue == -1):
                    empty_cell_blue = i
                elif (empty_cell_gold == -1):
                    empty_cell_gold = i

        if not blue:
            range_name = f"Ref Scoring!A{(row_num + 5) if empty_cell_blue == -1 else (empty_cell_blue + 4)}:A{(row_num + 5) if empty_cell_blue == -1 else (empty_cell_blue + 4)}"
            body = {
                'values': [[match_number]]
            }
            spreadsheet.values().update(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
                range=range_name, body=body, valueInputOption="RAW").execute()
        if not gold:
            range_name = f"Ref Scoring!A{(row_num + 5 + (0 if blue else 1)) if empty_cell_gold == -1 else (empty_cell_gold + 4)}:A{(row_num + 5 + (0 if blue else 1)) if empty_cell_gold == -1 else (empty_cell_gold + 4)}"
            body = {
                'values': [[match_number]]
            }
            spreadsheet.values().update(spreadsheetId=CONSTANTS.SPREADSHEET_ID,
                range=range_name, body=body, valueInputOption="RAW").execute()
