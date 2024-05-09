import os
from tkinter import messagebox
import ttkbootstrap as tb
import collections
import json
from configparser import ConfigParser
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from models import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv, find_dotenv

config = ConfigParser()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/admin.directory.device.chromeos"]
with open(r'configuration\config.ini', 'r') as f:
        config.read_file(f)
SERVICE_ACCOUNT_FILE = config['GOOGLE API']['serviceaccount']



file = json.load(open(SERVICE_ACCOUNT_FILE))

f = open(".env", "w")

for key, value in file.items():
    f.write(f"{key.upper()}={value}\n")

load_dotenv()

def create_keyfile_dict():
    variables_keys = {
        "type": os.getenv("TYPE"),
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL")
    }
    return variables_keys


def dev_sync(engine):
  
  table_devices = []
  stmt=select(Chromebook.device_sn, Chromebook.status)
  with Session(engine) as session:
    for row in session.execute(stmt):
      for tup in row:
        lst = [tup[0], tup[1]]
        table_devices.append(lst)
  
  #Using credentials from service account
  creds=service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

  service = build("admin", "directory_v1", credentials=creds)

  # Call the Admin SDK Directory API
  request = (
      service.chromeosdevices()
      .list(customerId = 'C033rjmnd', maxResults='500')
  )
  results = request.execute()
  devices = results.get('chromeosdevices', [])
  while request:
    request = service.chromeosdevices().list_next(previous_request=request, 
                                                  previous_response=results)
    if request:
      results = request.execute()
      devices.extend(results.get('chromeosdevices', []))

  data=[]

  if not devices:
    messagebox.showinfo(message='No devices in the domain!')
  else:
    for device in devices:
      #Handles if editable fields are empty and not in dictionary
      device.setdefault('annotatedLocation', None)
      device.setdefault('annotatedAssetId', None)
      device.setdefault('model', None)
      data.append(device)

  for device in data:
    if device['serialNumber'] not in table_devices:
      chrmbk = Chromebook(device['serialNumber'], device['annotatedLocation'], device['annotatedAssetId'], device['model'], device['status'])
      session.add(chrmbk)
  
  try:
     session.commit()
     session.close()
     messagebox.showinfo(message='Sync Succesful!')
  except Exception as e:
     session.rollback()
     session.close()
     messagebox.showerror(message='Unable to complete sync\n' + str(e))

if __name__ == "__main__":
  dev_sync()