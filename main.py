from __future__ import print_function
import io
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import auth

SCOPES = ['https://www.googleapis.com/auth/drive']

authInstance = auth.auth(SCOPES)

creds = authInstance.getCredentials()

drive_service = build('drive', 'v3', credentials=creds)

def listFiles(size):
    results = drive_service.files().list(
        pageSize=size, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


def uploadFile(fileName, filePath, mimeType):
    file_metadata = {'name': fileName}
    media = MediaFileUpload(filePath,
                            mimetype=mimeType)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print('File ID: %s' % file.get('id'))


def downloadFile(fileID, filePath):
    request = drive_service.files().get_media(fileId=fileID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    with io.open(filePath, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())


def createFolder(name):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()
    print('Folder ID: %s' % file.get('id'))

# downloadFile('1sdu_5m0p_tjALC3Iy2IjG3wKvPOfKAKB', 'aku.jpeg')