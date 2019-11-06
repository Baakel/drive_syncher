#!/home/baakel/PycharmProjects/drive_project/venv/bin/python
from __future__ import print_function
import io, os
import pickle
# import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import auth
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/drive']
token_path = '/home/baakel/PycharmProjects/drive_project/'

authInstance = auth.auth(SCOPES, token_path)

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


def uploadFile(fileName, filePath, mimeType, folder_id):
    file_metadata = {
        'name': fileName,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filePath,
                            mimetype=mimeType)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print(f'File ID: {file.get("id")}, File Name: {fileName}')


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


def searchFile(size, queryString):
    results = drive_service.files().list(
        pageSize=size, fields="nextPageToken, files(id, name, parents, trashed)",q=queryString).execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1}) parents {2} trashed {3}'.format(item['name'], item['id'], item['parents'], item['trashed']))


def getBgImages(folder_id):
    page_token = None
    while True:
        response = drive_service.files().list(q=f"'{folder_id}' in parents",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name, parents, mimeType, trashed, modifiedTime)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            # print(f'Found file: {file.get("name")} ({file.get("id")}) and parent is \u001b[31m{file.get("parents")}\u001b[0m and type is \u001b[32m{file.get("mimeType")}\u001b[0m')
            yield({'name': file.get('name'), 'trashed': file.get('trashed'), 'modified' : file.get('modifiedTime'), 'id': file.get('id')})
        # print(f'and there are {len(response.get("files", []))} files')
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break


def synchro(path, drive_id):
    files_in_comp = os.listdir(path)
    images = [i for i in getBgImages(drive_id)]
    images_list = []
    for image in images:
        for index in range(len(images)):
            if image['name'] == images[index]['name'] and image['trashed'] != images[index]['trashed']:
                if image['trashed'] == False:
                    images_list.append(images[index])
                elif image['trashed'] == True:
                    pass

    for removed_img in images_list:
        if removed_img in images:
            images.remove(removed_img)

    for image in images:
        # print(f'image is {image}')
        if image['name'] in files_in_comp and image['trashed'] is False:
            files_in_comp.remove(image['name'])
            continue
        elif image['name'] in files_in_comp and image['trashed'] is True:
            os.remove(f'{path}{image["name"]}')
            files_in_comp.remove(image['name'])
            print(f'deleting {image["name"]}')
        elif image['name'] not in files_in_comp and image['trashed'] is False:
            downloadFile(image['id'], f'{path}{image["name"]}')

    for file in files_in_comp:
        uploadFile(file, f'{path}{file}', 'image/', drive_id)

    print(f'Synchronization for {drive_id} finished at {datetime.now()}')

# getBgImages()
# searchFile(50, "name contains 'Bg'")
# downloadFile('1sdu_5m0p_tjALC3Iy2IjG3wKvPOfKAKB', 'aku.jpeg')

phone_folder_id = '0B1hcvlfr-rD-OGM2Zmp4b3hSeWs'
bg_folder_id = '0B1hcvlfr-rD-TXFlWWNKdFJyMnM'
test_api_folder_id = '1izt4ar8QAtoDcbpa_ssO8s9dJXdoqGhq'
ref_api_folder_id = '1Gtck3yl4EoRd0cjhcCkAvoTrnjQwxBsE'
bg_path = '/home/baakel/Drive/Bg/'
phone_path = '/home/baakel/Drive/Phone/'
test_path = '/home/baakel/Drive/test/'
ref_path = '/home/baakel/Drive/Reference/'

# getBgImages(test_api_folder_id)
# searchFile(10, "name contains 'aku'")


if __name__ == '__main__':
    synchro(phone_path, phone_folder_id)
    synchro(bg_path, bg_folder_id)
    synchro(ref_path, ref_api_folder_id)
    # synchro(test_path, test_api_folder_id)
