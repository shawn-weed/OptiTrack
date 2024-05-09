import os
from tkinter import messagebox
import ttkbootstrap as tb
import collections
import json
from configparser import ConfigParser
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from models import *
from dotenv import load_dotenv
from threading import Thread

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account

class Sync(tb.Toplevel):
    def __init__(self, engine):
      tb.Toplevel.__init__(self, title='Sync')
      self.engine = engine
      self.geometry('500x400')

      self.sync_frm = tb.Frame(self)
      self.sync_lbl = tb.Label(self.sync_frm,
                               text='Sync chromebooks now?',
                               font=('Helvetica', 20, 'bold'))
      self.warn_lbl = tb.Label(self.sync_frm,
                               text='This may take a few minutes',
                               font=('Helvetica', 16))
      self.sync_frm.pack(expand=True)
      self.sync_lbl.pack()
      self.warn_lbl.pack()

      self.sync_btn = tb.Button(self.sync_frm, text='Sync Now', command=self.show_gauge, bootstyle='danger')
      self.sync_btn.pack(pady=5)

      self.api_result = False

    def disable_event(self):
       pass

    def show_gauge(self):

      self.sync_frm.destroy()
      self.protocol("WM_DELETE_WINDOW", self.disable_event)

      self.wait_frm = tb.Frame(self)
      self.wait_frm.pack(expand=True)
      self.wait_lbl = tb.Label(self.wait_frm, text='Sync In Progress...', font=(None, 18, 'bold'))
      self.wait_lbl.pack()
      self.wait_gauge = tb.Floodgauge(self.wait_frm, bootstyle='danger', 
                                font=(None, 16,), 
                                mode = 'indeterminate', 
                                text='This May Take A Few Moments',
                                length=400)
      self.wait_gauge.pack()
      self.wait_gauge.start()

    def dev_sync(self):
      
      config = ConfigParser()
      # If modifying these scopes, delete the file token.json.
      SCOPES = ["https://www.googleapis.com/auth/admin.directory.device.chromeos",]

      with open(r'configuration\config.ini', 'r') as f:
            config.read_file(f)
      SERVICE_ACCOUNT_FILE = config['GOOGLE API']['serviceaccount']

      load_dotenv()

      file = json.load(open(SERVICE_ACCOUNT_FILE))

      f = open(".env", "w")

      for key, value in file.items():
          f.write(f"{key.upper()}={value}\n")


      table_devices = []
      stmt=select(Chromebook.device_sn, Chromebook.status)
      with Session(self.engine) as session:
        for row in session.execute(stmt):
          for tup in row:
            dct = {'sn': tup[0], 'status': tup[1]}
            table_devices.append(dct)
        
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
        self.devices = results.get('chromeosdevices', [])
        while request:
          request = service.chromeosdevices().list_next(previous_request=request, 
                                                        previous_response=results)
          if request:
            results = request.execute()
            self.devices.extend(results.get('chromeosdevices', []))

        data=[]

        if not self.devices:
          messagebox.showinfo(message='No devices in the domain!')
        else:
          for device in self.devices:
            #Handles if editable fields are empty and not in dictionary
            device.setdefault('annotatedLocation', None)
            device.setdefault('annotatedAssetId', None)
            device.setdefault('model', None)
            data.append(device)

        for device in data:
            result = session.query(Chromebook).filter_by(device_sn=device['serialNumber']).one_or_none()
            if result == None:
              chrmbk = Chromebook(device['serialNumber'], device['annotatedLocation'], device['annotatedAssetId'], device['model'], device['status'], condition='Serviceable', con_date=None, damage_notes=None)
              if chrmbk.status == 'DISABLED':
                 chrmbk.condition = 'Unserviceable'
              elif chrmbk.status == 'DEPROVISIONED':
                 chrmbk.condition = 'Unserviceable'
              session.add(chrmbk)
            elif result.status != device['status']:
              result.status = device['status']
              if result.status == 'DEPROVISIONED':
                 result.condition = 'Unserviceable'
              elif result.status == 'DISABLED':
                 result.condition = 'Unserviceable'
              session.flush()
        
        try:
          session.commit()
          session.close()
          self.finish()
        except Exception as e:
          session.rollback()
          session.close()
          messagebox.showerror(message='Unable to complete sync\nPlease Try Again\n' + 'Error: ' + str(e))
    
    def finish(self):  
         self.wait_gauge.stop()
         self.wait_frm.destroy()
         frm = tb.Frame(self)
         frm.pack(expand=True)
         suc_lbl = tb.Label(frm, text='Sync Successful!', font=('Helvetica', 20, 'bold'))
         close_lbl = tb.Label(frm, text='Please Close This Window to Continue', font=('Helvetica', 12))
         suc_lbl.pack(pady=5)
         close_lbl.pack(pady=5)
         close_btn = tb.Button(frm, text='Click To Close', command=lambda:self.destroy(), bootstyle='danger')
         close_btn.pack(pady=5)
        

    def cus_sync(engine):
      # If modifying these scopes, delete the file token.json.
      SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]

      load_dotenv()

      with open(r'configuration\config.ini', 'r') as f:
            config.read_file(f)
      SERVICE_ACCOUNT_FILE = config['GOOGLE API']['serviceaccount']

      file = json.load(open(SERVICE_ACCOUNT_FILE))

      f = open(".env", "w")

      for key, value in file.items():
          f.write(f"{key.upper()}={value}\n")

      #Using credentials from service account
      creds=service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

      service = build("admin", "directory_v1", credentials=creds)

      # Call the Admin SDK Directory API
      print("Getting the users in the domain")
      results = (
          service.users()
          .list(customer= 'C033rjmnd', maxResults='500', orderBy="email")
          .execute()
      )
      users = results.get("users", [])
      while request:
        request = service.users().list_next(previous_request=request, 
                                            previous_response=results)
        if request:
          results = request.execute()
          users.extend(results.get('users', []))
      
      if not users:
        messagebox.showinfo(message='No devices in the domain!')
      else:
        print("Users:")
        for user in users:
          print(f"{user['primaryEmail']} ({user['name']['fullName']})")