from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class auth:

    def __init__(self, SCOPES, TOKEN_PATH):  #,CLIENT_SECRET_FILE, APP_NAME):
        self.SCOPES = SCOPES
        self.TOKEN_PATH = TOKEN_PATH
        # self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        # self.APP_NAME = APP_NAME

    def getCredentials(self):
        """Shows basic usage of the Drive v3 API.
           Prints the names and ids of the first 10 files the user has access to.
           """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.TOKEN_PATH + 'token.pickle'):
            with open(self.TOKEN_PATH + 'token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds