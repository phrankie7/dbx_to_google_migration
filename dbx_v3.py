import os
import dropbox
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

local_path = r"C:\Users\defaultuser0\Desktop\dbx_local"

# Replace with your Dropbox access token
DROPBOX_ACCESS_TOKEN = 'sl.B7lCjty-siIM6T-YimxkO16TzXo8ueOQC-LnPJIdgFEjBJ_Lr-_ox7uL_kOlorLCyIUEcu2eImtQK0BOpWOq42Q6bcEk2elGWKQo8u68U3W2pUKCsp4VXVoVSIoV89j88KEA'

# Replace with the path to your Google Service Account credentials file
SERVICE_ACCOUNT_FILE = r"C:\Users\defaultuser0\Downloads\projectcorpt-29a4f166fefa.json"

# Google Drive folder ID where you want to upload the files
GOOGLE_DRIVE_FOLDER_ID = '1awzXmy0rBsFs52W1Xm'

# Dropbox folder path to migrate from
DROPBOX_FOLDER_PATH = '/CorpT'

# Set up Dropbox client
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Set up Google Drive client
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Download files from Dropbox
def download_file_from_dropbox(dbx, dropbox_path, local_path):
    open(local_path, "wb").write(dbx.files_download(path=dropbox_path)[1].content)
    return local_path

def upload_file_to_google_drive(drive_service, local_path, folder_id=None):
    return drive_service.files().create(
        body={'name': os.path.basename(local_path), 'parents': [folder_id]} if folder_id else {'name': os.path.basename(local_path)},
        media_body=MediaFileUpload(local_path, resumable=True),
        fields='id'
    ).execute().get('id')

def migrate_dropbox_to_google_drive(dbx, drive_service, dropbox_folder_path, google_drive_folder_id=None):
    result = dbx.files_list_folder(dropbox_folder_path, recursive=True)
    
    while True:
        for entry in result.entries:
            dropbox_file_path = entry.path_lower
            local_file_path = os.path.join(local_path, entry.name)

            if isinstance(entry, dropbox.files.FileMetadata):  # Ensure it's a file, not a folder
                # Download file from Dropbox
                download_file_from_dropbox(dbx, dropbox_file_path, local_file_path)

                # Upload file to Google Drive
                upload_file_to_google_drive(drive_service, local_file_path, google_drive_folder_id)

                # Clean up local file after upload
                os.remove(local_file_path)

            elif isinstance(entry, dropbox.files.FolderMetadata):  # It's a folder
                # Create the corresponding local folder if it doesn't exist
                folder_local_path = os.path.join(local_path, entry.name)
                if not os.path.exists(folder_local_path):
                    os.makedirs(folder_local_path)

        # Check if there are more pages
        if result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
        else:
            break

# Run the migration
migrate_dropbox_to_google_drive(dbx, drive_service, DROPBOX_FOLDER_PATH, GOOGLE_DRIVE_FOLDER_ID)

print('File migration complete !!')
