import configuration.configuration as configuration
from configparser import ConfigParser
from tkinter import *
from PIL import Image
Image.CUBIC = Image.BICUBIC
from tkcalendar import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from windowassets import Header
from models import *
from pages import *
from windowassets import Header, AssignedMeter
from ttkbootstrap import StringVar, IntVar
from serverconfig import *
from SQLconnection import *
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


class MainApp(tb.Window):
   def __init__(self, *args, **kwargs):
      tb.Window.__init__(self, *args, **kwargs)

      self.config = ConfigParser()

      self.header = Header(self, r'assets\Liberty_headerlogo.png', 500, 100, 'inverse-light')

      self.left_container = tb.Frame(self, width = 150, bootstyle = 'dark')
      self.left_container.pack(side = 'left', fill = tb.Y)
      
      self.right_container = tb.Frame(self, width = 150)
      self.right_container.pack(side = 'right', fill = tb.Y)
      
      self.wm_title("OptiTrack")
      self.geometry('')

      # creating a frame and assigning it to container
      self.container = tb.Frame(self, height=400, width=700)
      
      # specifying the region where the frame is packed in root
      self.container.pack(side="top", fill="both", expand=True)

      # configuring the location of the container using grid
      self.container.grid_rowconfigure(0, weight=1)
      self.container.grid_columnconfigure(0, weight=1)


      self.overall_mtr = tb.Meter(self.right_container, metersize=150, padding=5, metertype='semi', subtext='Assigned', textright='of ' + '', bootstyle='danger')
      self.hs_mtr = tb.Meter(self.right_container, metersize=150, padding=5, metertype='semi', subtext='HS Assigned', textright = 'of ' + '', bootstyle='danger')
      self.ms_mtr = tb.Meter(self.right_container, metersize=150, padding=5, metertype='semi', subtext='MS Assigned', textright = 'of ' + '', bootstyle='danger')
      self.es_mtr = tb.Meter(self.right_container, metersize=150, padding=5, metertype='semi', subtext='ES Assigned', textright = 'of ' + '', bootstyle='danger')

      self.overall_mtr.pack()
      self.hs_mtr.pack()
      self.ms_mtr.pack()
      self.es_mtr.pack()  

      #will open config file if there is one. If not it will write from serverconfig.py
      with open(r'configuration\hostconfig.ini', 'r') as f:
         self.config.read_file(f)
      #if a connection has not been establish it will start from here
      try:
         if 'CONNECTION' not in self.config.sections():
            self.show_config_window()
         #If a connection has been entered before 
         else:
            if self.config['CONNECTION']['software'] == 'mssql': #For using sql server login creds
               if self.config['CONNECTION']['connectiontype'] == 'win': #for using windows authentication
                  self.conn = WinConn(self.config['CONNECTION']['server'], self.config['CONNECTION']['db'])
                  self.cnxn = self.conn.engine.connect()
                  self.engine = self.conn.engine
                  try:
                     Session = sessionmaker(bind=self.engine)
                     self.session = Session()
                  except Exception as e:
                     messagebox.showerror(message='Unable to connect to Database:\n' + str(e))
                  self.start_main()
               else:
                  self.show_config_window()
                  self.connselect.set(1)
                  self.db_show_frame(MSSqlConfig)
                  self.dbframes[MSSqlConfig].server_ent.insert(0, self.config['CONNECTION']['server'])
                  self.dbframes[MSSqlConfig].server_ent.configure(state='disabled')
               
                  self.dbframes[MSSqlConfig].db_ent.insert(0, self.config['CONNECTION']['db'])
                  self.dbframes[MSSqlConfig].db_ent.configure(state='disabled')
      except Exception as e:
         self.create_popup = messagebox.askquestion(message='No tables found in database.\n Would you like to create them?')
         if self.create_popup == 'yes':
            Base.metadata.create_all(self.engine)
            self.start_main()

   def show_config_window(self):
      self.iconify()
      self.config_win = tb.Toplevel(self)
      self.dbframes = {}

      for DF in (Begin,
                MSSqlConfig,
                ):
         frame = DF(self.config_win, self)
         self.dbframes[DF] = frame
         frame.grid(row=0, column=0, sticky='nsew')

      self.db_show_frame(Begin)
      self.grab_set()

      self.connselect = self.dbframes[Begin].connselect
      self.connselect.trace_add('write', self.get_connection)

   def get_connection(self, var, index, mode):
      if self.connselect.get() == 1:
         self.validconnection = self.dbframes[MSSqlConfig].validconnection
         self.validconnection.trace_add('write', lambda x, y, z: [self.set_connection(x, y, z), Base.metadata.create_all(self.engine), self.start_main(x, y, z),])

   def set_connection(self, var, index, mode):
      if self.connselect.get() == 1:
         self.cnxn = self.dbframes[MSSqlConfig].cnxn
         self.engine = self.dbframes[MSSqlConfig].conn.engine
         Session = sessionmaker(bind=self.engine)
         self.session = Session()

   def db_show_frame(self, cont):
      frame = self.dbframes[cont]
      frame.tkraise()

   def show_frame(self, cont):
      frame = self.frames[cont]
      # raises the current frame to the top
      frame.tkraise()

   def check_connection(self):
      self.after(1200000, self.check_connection)
      try:
        # db.session.execute('SELECT 1')
        self.session.execute(text('SELECT 1'))
      except Exception as e:
         popup = messagebox.askyesno(message='Connection has timed out. Reconnect?')
         if popup == True:
            self.show_config_window()
         else:
            app.destroy()
   
   def update_meters(self):
      try:
         self.total_meter.update()
         self.es_meter.update()
         self.ms_meter.update()
         self.hs_meter.update()
         self.after(5000, self.update_meters)
      except:
         messagebox.showerror(message='Unable to update meters')

   def start_main(self, var=None, index=None, mode=None):
      self.overall_mtr.destroy()
      self.hs_mtr.destroy()
      self.ms_mtr.destroy()
      self.es_mtr.destroy()

            # Creates a dictionary for frames
      self.frames = {}
      
      #Puts frames into dictionary
      for F in (MainMenu, 
               SearchPage,
               SettingsPage 
               ):
         frame = F(self.container, self)
            # the MainApp class acts as the root window for the frames.
         self.frames[F] = frame
         frame.grid(row=0, column=0, sticky="nsew") 

      self.show_frame(MainMenu)
      self.config_win.destroy()
      self.deiconify()
      
      self.home_btn = tb.Button(self.left_container, text='Home', command=lambda: self.show_frame(MainMenu), bootstyle='light-outline', width=20)
      self.search_btn = tb.Button(self.left_container, text='Chromebooks', command=lambda: self.show_frame(SearchPage), bootstyle='light-outline', width=20)
      self.settings_btn = tb.Button(self.left_container, text='Settings', command=lambda: self.show_frame(SettingsPage), bootstyle='light-outline', width=20)

      self.home_btn.pack(fill=tb.X)
      self.search_btn.pack(fill=tb.X)
      self.settings_btn.pack(fill=tb.X)

      self.total_meter = AssignedMeter(self.right_container, self.engine)
      self.hs_meter = AssignedMeter(self.right_container, self.engine, school='HS')
      self.ms_meter = AssignedMeter(self.right_container, self.engine, school='MS')
      self.es_meter = AssignedMeter(self.right_container, self.engine, school='ES')
      
      self.total_meter.pack()
      self.hs_meter.pack()
      self.ms_meter.pack()
      self.es_meter.pack()

      self.check_connection()
      self.update_meters()

if __name__ == "__main__":

   app = MainApp(themename='darkly')
   app.mainloop()
