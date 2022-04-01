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
from ydl import ydl_send
from utils import YDL_TARGETS, SHEPHERD_HEADER, CONSTANTS

# If modifying these scopes, delete your previously saved credentials
# at USER_TOKEN_FILE
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRET_FILE = 'sheets/client_secret.json'
USER_TOKEN_FILE = "sheets/user_token.json" # user token; do not upload to github (.gitignore it)

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
                    range="Match Database!A2:N").execute()['values']
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Fetching data from offline csv file")
                with open(CONSTANTS.CSV_FILE_NAME) as csv_file:
                    game_data = list(csv.reader(csv_file, delimiter=','))[1:]

            return_len = 14
            lst = [""] * return_len
            for row in game_data:
                if len(row) > 0 and row[0].isdigit() and int(row[0]) == match_number:
                    lst = row[1:return_len+1] + [""]*(return_len+1-len(row))
                    break
            teams = [{},{},{},{}]
            for a in range(4):
                teams[a]["team_num"] = int(lst[3*a+1]) if lst[3*a+1].isdigit() else -1
                teams[a]["team_name"] = lst[3*a+2]
                teams[a]["robot_ip"] = lst[3*a+3]
            ydl_send(*SHEPHERD_HEADER.SET_TEAMS_INFO(teams=teams))

        threading.Thread(target=bg_thread_work).start()

    @staticmethod
    def read_scores(match_number):
        def bg_thread_work():
            try:
                Sheet.__read_online_scores(match_number)
            except: # pylint: disable=bare-except
                print('[error!] Google API has changed yet again, please fix Sheet.py')
                print("Unable to write to spreadsheet")
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
                        ydl_send(*SHEPHERD_HEADER.SEND_SCORES(scores=[blue, gold]))
                        return
                elif row[1] == "Gold":
                    gold = row[2]
                    if blue is not None and gold is not None:
                        ydl_send(*SHEPHERD_HEADER.SEND_SCORES(scores=[blue, gold]))
                        return

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
