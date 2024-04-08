import ttkbootstrap as tb
from tkinter import messagebox, StringVar, IntVar
from configparser import ConfigParser
from SQLconnection import WinConn, MSSQLConn
from windowassets import UsernameEntry
from pages import MainMenu

class ServerConfig:
    def __init__(self, configFile):
        self.configFile = configFile
        self.config = ConfigParser()

    def write_file(self):  
        self.config.write(open(self.configFile, 'w'))

    def read_config(self):
        self.config.read(self.configFile)

    def getServers(self):
        return self.config.sections()
    
    def getData(self, host, key):
        return self.config[host][key]
    
    def getHostDetails(self, host):
        hostdata = self.config[host]
        return hostdata['server'], hostdata['db']

class Begin(tb.Frame):
    def __init__(self, parent, controller):
        tb.Frame.__init__(self, parent)
        self.controller = controller

        #opens config file if present, if not it will be created from configuration.py
    
        #Frame to hold all widgets on Begin page
        self.begin_frm = tb.Frame(self)
        self.begin_lbl = tb.Label(self.begin_frm, text='Connect to Database', font=('hellvetica', 25, 'bold'))
        
        #Creates variable to trace of an old or new connection will be used. 
        self.connselect = IntVar()
        self.connselect.trace_add('write', lambda x, y, z: [self.db_selection(x, y, z), self.begin_btn.focus_set()])

        mssql_radio = tb.Radiobutton(self.begin_frm, text='SQL Server', variable=self.connselect, value=1)
        self.begin_btn = tb.Button(self.begin_frm, text='Select', bootstyle='light')
        self.begin_btn.bind('<Return>', lambda x: self.begin_btn.invoke) #Binds return button to begin button and commands same function
        
        self.begin_frm.pack(expand=True)
        self.begin_lbl.pack(pady=20)
        mssql_radio.pack(pady=10, anchor='w')
        self.begin_btn.pack(pady=10, ipadx=20)

        
        #Takes arguments from connselect trace
    def db_selection(self, var, index, mode):
        if self.connselect.get() == 1: # 1 == MSSql set up
            self.begin_btn.configure(command=lambda: self.controller.db_show_frame(MSSqlConfig))

class MSSqlConfig(tb.Frame):
    def __init__(self, parent, controller):
        tb.Frame.__init__(self, parent)
        self.controller = controller
        self.serverconfig = ServerConfig('hostconfig.ini')

        self.validconnection = StringVar()
        
        #Creates variables to retain info from entry boxes
        self.server = StringVar()
        self.db = StringVar()
        
        #Creates frame and entry boxes for configuration
        self.config_frm = tb.Frame(self)
        config_lbl = tb.Label(self.config_frm, text='SQL Server Configuration', font=('helvetica', 24, 'bold'))
        self.server_lbl = tb.Label(self.config_frm, text = 'Server Name/IP address')
        self.server_ent = tb.Entry(self.config_frm, textvariable=self.server)
        self.db_lbl = tb.Label(self.config_frm, text = 'Database Name')
        self.db_ent = tb.Entry(self.config_frm, textvariable=self.db)
        
        #Packs fields onto screen
        self.config_frm.pack(expand=True)
        config_lbl.pack()
        self.server_lbl.pack()
        self.server_ent.pack()
        self.db_lbl.pack()
        self.db_ent.pack()

        #Traces radio buttons. Once selected Submit is focused so return key binding can be used to invoke submit button
        self.radio_var = IntVar()
        self.radio_var.trace_add('write', callback=self.select_mssql_type)

        radio_frm = tb.Frame(self.config_frm)
        sql_radio = tb.Radiobutton(radio_frm, text='Login with MSSql credentials', variable=self.radio_var, value = 1)
        win_radio = tb.Radiobutton(radio_frm, text='Login with Windows Authorization', variable=self.radio_var, value= 2)

        #packs buttons for login type
        radio_frm.pack(pady=5)
        sql_radio.pack(pady=5, anchor='w')
        win_radio.pack(pady=5)

        #Variables for logins creds
        self.username = StringVar()
        self.pw = StringVar()
        self.save_user = IntVar()

        cred_frm = tb.Frame(self.config_frm)
        
        self.sql_lbl = tb.Label(cred_frm, text='Username')
        self.sql_ent = UsernameEntry(cred_frm, textvariable=self.username, state='disabled', bootstyle='dark')
        
        self.pw_lbl = tb.Label(cred_frm, text='Password', )
        self.pw_ent = tb.Entry(cred_frm, textvariable=self.pw, show='\u2022', state='disabled', bootstyle='dark')
        self.pw_ent.bind('<Return>', lambda e: self.sb_btn.invoke())
        save_user = tb.Checkbutton(cred_frm, text='Save Username', variable=self.save_user, offvalue=0, onvalue=1)
        
        btn_frm = tb.Frame(cred_frm)
        self.sb_btn = tb.Button(btn_frm, text='Connect', bootstyle='light')
        back_btn = tb.Button(btn_frm, text='Back', bootstyle='light')

        cred_frm.pack(expand=True)
        
        self.sql_lbl.pack()
        self.sql_ent.pack(pady=5)

        self.pw_lbl.pack()
        self.pw_ent.pack(pady=5)

        save_user.pack()
        
        btn_frm.pack(pady=10)
        back_btn.pack(side='left', padx=5, ipadx=3)
        self.sb_btn.pack(side='right', padx=5)
    
    def submit_mssql_creds(self):
        if self.server.get() == '': 
            messagebox.showinfo(message='Connection details are required')
            self.server_lbl.configure(bootstyle='danger')
        elif self.db.get() == '':
            messagebox.showinfo(message='Connection details are required')
            self.db_lbl.configure(bootstyle='danger')
        elif self.username.get() == '':
            messagebox.showinfo(message='Username is required')
            self.sql_lbl.configure(bootstyle='danger')
        elif self.pw.get() == '':
            messagebox.showinfo(message='Please enter a password')
            self.pw_lbl.configure(bootstyle='danger')
        else:
        
            self.conn = MSSQLConn(self.server.get().strip(), 
                            self.db.get().strip(), 
                            self.username.get().strip(),
                            self.pw.get().strip())
            try:
                self.cnxn = self.conn.engine.connect()
                self.validconnection.set('True')

            except Exception as e:
                messagebox.showerror(message= 'Unable to connect:\n' + str(e))
                
            try:    
                self.serverconfig.read_config()

                if 'CONNECTION' not in self.serverconfig.getServers():   
                    self.serverconfig.config.add_section('CONNECTION')
                self.serverconfig.config.set('CONNECTION', 'software', 'mssql')
                self.serverconfig.config.set('CONNECTION', 'connectiontype', 'MSSql')
                self.serverconfig.config.set('CONNECTION', 'server', self.server.get().strip())
                self.serverconfig.config.set('CONNECTION', 'db', self.db.get().strip())
                self.serverconfig.config.set('CONNECTION', 'username', '')
                with open('hostconfig.ini', 'w') as configfile:
                    self.serverconfig.config.write(configfile)

                #writes username to config file
                if self.save_user.get() == 1:
                    self.config.set('CONNECTION', 'username', self.username.get().strip())
                    with open('hostconfig.ini', 'w') as configfile:
                        self.serverconfig.config.write(configfile)

            except Exception as e:
                messagebox.showerror(message= 'Unable to save connection configuration:\n' + str(e))

    def select_mssql_type(self, var, index, mode):
        if self.radio_var.get() == 1:
            self.sql_ent.configure(state='normal', bootstyle='light')
            self.pw_ent.configure(state='normal', bootstyle='light')
            self.sb_btn.configure(command=self.submit_mssql_creds)
            self.sb_btn.focus_set() #Puts focus on button to use binding with return key
        elif self.radio_var.get() == 2:
            self.sql_ent.configure(state='disabled', bootstyle='dark')
            self.pw_ent.configure(state='disabled', bootstyle='dark')
            self.sb_btn.configure(command=self.start_win)
            self.sb_btn.focus_set()


    def start_win(self):

      if self.server.get() == '':
          messagebox.showinfo(message='Connection details must not be blank')
          self.server_lbl.configure(bootstyle='danger')
          self.db_lbl.configure(bootstyle='danger')
      if self.db.get() == '':
          messagebox.showinfo(message='Connection details must not be blank')
          self.server_lbl.configure(bootstyle='danger')
          self.db_lbl.configure(bootstyle='danger')
      else:
            self.conn = WinConn(self.server.get(), self.db.get())
            try:
                self.cnxn = self.conn.engine.connect()
                self.validconnection.set('True')

            except Exception as e:
                messagebox.showerror(message='Unable to establish connection:\n' + str(e))    
                
            try:    
                self.serverconfig.read_config()

                if 'CONNECTION' not in self.serverconfig.getServers():
                    self.serverconfig.config.add_section('CONNECTION') 
                self.serverconfig.config.set('CONNECTION', 'software', 'mssql')
                self.serverconfig.config.set('CONNECTION', 'connectiontype', 'win')
                self.serverconfig.config.set('CONNECTION', 'server', self.server.get())
                self.serverconfig.config.set('CONNECTION', 'db', self.db.get())
                with open('hostconfig.ini', 'w') as configfile:
                    self.serverconfig.config.write(configfile)
            except Exception as e:
                messagebox.showerror(message='Unable to save connection configuration:\n' + str(e))

