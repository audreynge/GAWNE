import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

def authenticate():
  """Handles authentication and then returns the Drive API service"""
  creds = None

  # token.json stores the user's access and refresh tokens, and is created 
  # automatically when the authorization flow completes for the first time
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  # if there are no (valid) credentials available, let the user log in
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  # return the drive api service
  return build("drive", "v3", credentials=creds)

def get_shared_folder_id(service, folder_name):
  """Returns the ID of a folder in 'Shared with me'"""
  query = f"sharedWithMe = true and mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}'"
  results = service.files().list(q=query, fields="files(id, name)").execute()
  folders = results.get("files", [])

  if not folders:
    print(f"folder '{folder_name} not found in Shared with me")
    return None

  return folders[0]['id']

def list_files_in_folder(service, folder_id):
  """Lists files from the given folder ID"""
  query = f"'{folder_id}' in parents"
  results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
  files = results.get("files", [])

  if not files:
    print(f"no files found in folder {folder_id}")
    return []

  for file in files:
    print(f"{file['name']} ({file['id']}) - mimeType: {file['mimeType']}")  # Print mimeType

  return files

def download_folder_contents(service, folder_id, folder_name):
  """Downloads all files from a folder (recursively if there are subfolders)"""
  print(f"Processing folder: {folder_name}")
  
  # Create a directory for the folder if it doesn't exist
  folder_path = os.path.join(os.getcwd(), folder_name)
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)
  
  # List all files in the folder
  files = list_files_in_folder(service, folder_id)
  
  for file in files:
    file_id = file['id']
    file_name = file['name']
    mime_type = file['mimeType']
    
    if mime_type == 'application/vnd.google-apps.folder':
      subfolder_path = os.path.join(folder_name, file_name)
      download_folder_contents(service, file_id, subfolder_path)
    else:
      download_file(service, file_id, file_name, folder_path)

def download_file(service, file_id, file_name, destination_folder):
  """Downloads a file from the given file ID and name or exports Docs files."""
  # Get the file's metadata
  request = service.files().get(fileId=file_id)
  file = request.execute()

  mime_type = file.get('mimeType')
  output_file_name = file_name

  if mime_type == 'application/vnd.google-apps.document':
    request = service.files().export(fileId=file_id, mimeType='application/pdf')
    output_file_name = file_name + '.pdf'  # Export as PDF
  elif mime_type == 'application/vnd.google-apps.spreadsheet':
    request = service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    output_file_name = file_name + '.xlsx'  # Export as XLSX
  elif mime_type == 'application/vnd.google-apps.presentation':
    request = service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    output_file_name = file_name + '.pptx'  # Export as PPTX
  else:
    # for regular files (.mov) use get_media
    request = service.files().get_media(fileId=file_id)

  file_path = os.path.join(destination_folder, output_file_name)

  try:
    # open the file + write the content to disk
    with open(file_path, "wb") as f:
      f.write(request.execute())
    print(f"Downloaded {output_file_name} to {file_path}")
  except Exception as e:
    print(f"Error downloading {file_name}: {str(e)}")


def main():
  service = authenticate()
  
  folder_name = "Test Drive"
  folder_id = get_shared_folder_id(service, folder_name)

  if folder_id:
    print(f"Found shared folder: {folder_name} with ID: {folder_id}")
    download_folder_contents(service, folder_id, folder_name)

if __name__ == "__main__":
  main()