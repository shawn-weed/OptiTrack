import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap import StringVar
from PIL import Image, ImageTk
Image.CUBIC = Image.BICUBIC
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Querybox
from sqlalchemy import text, or_, not_, select, exists
from SQLconnection import *
import tkinter.ttk as ttk
from tkinter import messagebox
import pandas as pd
from sqlalchemy.orm import sessionmaker
from models import Chromebook, Customer, Fact, History
from windowassets import InfoBox, SearchEntry
from datetime import datetime, date
from deviceQuery import *

class MainMenu(tb.Frame):
   def __init__(self, parent, controller):
      tb.Frame.__init__(self, parent)
      self.controller = controller

      label=tk.Label(self, text='LCSD Asset Management', font=('Garamond', 45, 'bold'))
      label.pack()

      image=Image.open(r'assets\Cover bird.png')
      resize_ph = image.resize((600,360))
      ph=ImageTk.PhotoImage(resize_ph)
      label=tb.Label(self, image=ph, text='OptiTrack')
      chromebooks_frm = tb.Frame(self)
      chromebooks_btn = tb.Button(chromebooks_frm, text= 'Manage Chromebooks', bootstyle='light-link', image=ph, compound='top', command=lambda: self.controller.show_frame(SearchPage))
      chromebooks_btn.image=ph
      chromebooks_btn.pack()
      chromebooks_frm.pack(expand=True)

class SearchPage(tb.Frame):
   def __init__(self, parent, controller):
      tb.Frame.__init__(self, parent)  
      self.controller = controller

      heading = tb.Label(self, text= 'Search for a Record', font=('Garamond', 50, 'bold'))
      heading.pack(pady=(0, 10))

      #Queries all available devices and joins any that are assigned in Fact table
      Session = sessionmaker(bind=self.controller.engine)
      self.session = Session()
      
      self.result = self.session.query(Chromebook, Fact).outerjoin(Fact).all()
      self.session.close()
      #Creates variable to load new table data based on combobox selection
      self.assign_var = StringVar()
      self.assign_var.trace_add('write', self.filter_table)

      #creates from for filter combobox
      filter_frm = tb.Frame(self)
      filter_frm.pack(fill=tb.X, pady=10)
      
      #Creates combobox and label to change table data
      assign_lbl = tb.Label(filter_frm, text='Filter by:', font=('Helvetca', 14))
      assign_cbx = tb.Combobox(filter_frm, textvariable=self.assign_var)
      assign_cbx['values'] = ['All',
                              'Assigned Only']
      assign_cbx.configure(state='readonly')
      assign_cbx.pack(side='right', padx=5)
      assign_lbl.pack(side='right', padx=5)

      #Sets up columns
      self.coldata =[{'text': 'Device S/N', 'stretch': True}, 
                     {'text': 'Asset Tag', 'stretch': True},
                     {'text': 'Building', 'stretch': True}, 
                     {'text': 'Status', 'stretch': True},
                     {'text': 'Assigned to', 'stretch': True}, 
                     {'text': 'Date Issued', 'stretch': True}, 
                     {'text': 'Loaner S/N', 'stretch': True}, 
                     {'text': 'Loaner Issue Date', 'stretch': True},
                     ]
      
      self.rowdata = []

      #iterates through query results to load into table
      for row in self.result:
         if row[1] != None:
            lst = [row.Chromebook.device_sn, 
                   row.Chromebook.asset_tag, 
                   row.Chromebook.building, 
                   row.Chromebook.status, 
                   row.Fact.email, 
                   row.Fact.date_issued, 
                   row.Fact.loaner_sn, 
                   row.Fact.loaner_issue_date,
                   ]

            #Takes all None type values and converts to empty string. This allows the tableview to be sorted
            for i in range(len(lst)):
               if lst[i] == None:
                  lst[i] = ''
         else:
           lst = [row.Chromebook.device_sn, 
                  row.Chromebook.asset_tag, 
                  row.Chromebook.building, 
                  row.Chromebook.status, 
                  '', 
                  '', 
                  '',
                  '',
                  ]
           for i in range(len(lst)):
               if lst[i] == None:
                  lst[i] = ''
         self.rowdata.append(lst)
      
      #Frame is here so when the TableView is pack_forget it will repack above the buttons
      self.tree_frm = tb.Frame(self)
      self.tree_frm.pack(expand=True, fill=BOTH)
      self.tree = Tableview(self.tree_frm, rowdata=self.rowdata, 
                            coldata=self.coldata, 
                            bootstyle='secondary',
                            pagesize=20, 
                            paginated=True, 
                            searchable=True, 
                            autofit=True,
                            autoalign=True, 
                            height=20,
                            stripecolor=('#3b3b3b', None),
                            )
      
      self.tree.pack(side=TOP, fill=BOTH)

      action_frm = tb.Frame(self)
      action_frm.pack()

      view_btn = tb.Button(action_frm, text='View', command=self.check_select_view)
      action_btn = tb.Button(action_frm, text='Action',)
      
      view_btn.pack(side='left', expand=True, padx=5, pady=5)
      action_btn.pack(side='left', expand=True, padx=5, pady=5)

   def check_select_view(self):
         if self.tree.focus() == '':
            tk.messagebox.showinfo(title=None, message="Please make a selection")
         else:
            self.selected = self.tree.get_rows(selected=True)
            #Query returns instance of Chromebook class for selected device
            try:
               Session = sessionmaker(bind=self.controller.engine)
               self.session = Session()
               self.device = self.controller.session.query(Chromebook).filter(Chromebook.device_sn == self.selected[0].values[0]).one_or_none()
               self.session.close()
               
               if self.selected[0].values[4] == '':
                  self.assigned = False
               else:
                  self.assigned = True
               viewpage = View(self.controller.container, self.controller, self.device, self.assigned)
               viewpage.grid(row=0, column=0, sticky='nsew')
            except Exception as e:
                  messagebox.showerror(message='Unable to retrieve device details:\n' + str(e))

   #Changes table data based on combobox selection
   def filter_table(self, var, index, mode):
      self.filtered_data = []
      if self.assign_var.get() == 'Assigned Only':
         for row in self.rowdata:
            if row[4] != '':
               self.filtered_data.append(row)
         self.tree.pack_forget()
         self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
         self.tree.reset_table()
         self.tree.pack()

      else:
         self.tree.pack_forget()
         self.tree.build_table_data(rowdata = self.rowdata, coldata=self.coldata)
         self.tree.reset_table()
         self.tree.pack()

class View(ScrolledFrame):

   #The selected device from the table on search page is passed through device parameter
   def __init__(self, parent, controller, device, assigned):
      super(View, self).__init__(parent)
      self.controller = controller
      self.device = device
      self.assigned = assigned
      
      #Slaved varaibles for selected deivce from search page
      self.sn_var = StringVar(value=self.device.device_sn)
      self.at_var = StringVar(value=self.device.asset_tag)
      self.bldg_var = StringVar(value=self.device.building)
      self.stat_var = StringVar(value=self.device.status) #Also used for radio buttons in return_dev method

      #Slaved variables for customer details. Only set if there is an assignment for device
      self.name_var = StringVar()
      self.id_var = StringVar()
      self.email_var = StringVar()
      self.role_var = StringVar()
      self.active_var = StringVar()
      self.iss_var = StringVar()
      
      #Slaved data for fact info. Only set if there is an assignment for device
      self.loan_var = StringVar()
      self.loan_sn_var = StringVar()
      self.l_iss_data_var =StringVar()

      #Creates variable to change color of person label depending on active status
      self.per_style = StringVar(value='secondary')

      # except Exception as e:
      #    messagebox.showinfo(message='Something went wrong') 

      self.title_font = ('default', 22, 'bold')
      self.sub_font = ('default', 12, 'bold')
      self.info_font = ('default', 12, 'normal')

      #dev style is set in update_dev_style method
      self.dev_style = StringVar()
      self.update_dev_style()
      #changes label color based on device status. 
      self.stat_var.trace_add('write', lambda x, y, z: (self.update_dev_style(), self.device_lbl.configure(bootstyle = f'inverse-{self.dev_style.get()}')))

      #Device Details
      self.device_lbl = tb.Label(self, text='Device Details', font=self.title_font, bootstyle = f'inverse-{self.dev_style.get()}')
      self.device_lbl.pack(fill=tb.X)
      self.device_frm = tb.Frame(self,)

      self.dev_label_frame = tb.Frame(self.device_frm)
      self.sn_lbl = tb.Label(self.dev_label_frame, text= 'Device S/N: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.at_lbl = tb.Label(self.dev_label_frame, text= 'Asset Tag: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.bldg_lbl = tb.Label(self.dev_label_frame, text= 'Building: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.stat_lbl = tb.Label(self.dev_label_frame, text= 'Status: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)

      self.dev_ent_frame = tb.Frame(self.device_frm)
      self.sn_ent = InfoBox(self.dev_ent_frame, textvariable=self.sn_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.at_ent = InfoBox(self.dev_ent_frame, textvariable=self.at_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.bldg_ent = InfoBox(self.dev_ent_frame, textvariable=self.bldg_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.stat_ent = InfoBox(self.dev_ent_frame, textvariable=self.stat_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)

      self.dev_btn_frm = tb.Frame(self.device_frm)
      self.status_btn = tb.Button(self.dev_btn_frm, text='Update Status', command=self.update_status, bootstyle='light').pack(expand=True, fill=BOTH)
      
      self.device_frm.pack(side=TOP, fill=tb.X, expand=True, anchor=W)
      self.dev_label_frame.pack(side=LEFT, fill=tb.Y, anchor=W)
      self.dev_ent_frame.pack(side=LEFT, fill=tb.X, anchor=W)
      self.dev_btn_frm.pack(side=LEFT, fill=BOTH, expand=True, anchor=W)
      
      #Customer details
      self.person_frm = tb.Frame(self)
      self.person_lbl = tb.Label(self.person_frm, text='Assigned To', font=self.title_font, bootstyle = f'inverse-{self.per_style.get()}')
      self.person_lbl.pack(fill=tb.X)

      #Adds trace to active variable to change person label color
      self.active_var.trace_add('write', lambda x, y, z: (self.update_per_style(), self.person_lbl.configure(bootstyle = f'inverse-{self.per_style.get()}')))

      self.person_lbl_frm = tb.Frame(self.person_frm,)
      self.name_lbl = tb.Label(self.person_lbl_frm, text = 'Name: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.id_lbl = tb.Label(self.person_lbl_frm, text='ID: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.email_lbl = tb.Label(self.person_lbl_frm, text='Email: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.role_lbl =tb.Label(self.person_lbl_frm, text='Role: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.active_lbl = tb.Label(self.person_lbl_frm, text='Active: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.iss_lbl = tb.Label(self.person_lbl_frm, text= 'Date Issued: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)

      self.person_ent_frm = tb.Frame(self.person_frm)
      self.name_ent = InfoBox(self.person_ent_frm, textvariable=self.name_var, width=50, font=self.info_font).pack(anchor=W)
      self.id_ent = InfoBox(self.person_ent_frm, textvariable=self.id_var, width=50, font=self.info_font).pack(anchor=W)
      self.email_ent = InfoBox(self.person_ent_frm, textvariable=self.email_var, width=50, font=self.info_font).pack(anchor=W)
      self.role_ent = InfoBox(self.person_ent_frm, textvariable=self.role_var, width=50, font=self.info_font).pack(anchor=W)
      self.active_ent = InfoBox(self.person_ent_frm, textvariable=self.active_var, width=50, font=self.info_font).pack(anchor=W)
      self.iss_date = tb.DateEntry(self.person_ent_frm, bootstyle='secondary', width=47, startdate=None)
      self.iss_date.entry.delete(0, END)
      self.iss_date.configure(state=READONLY)
      self.iss_date.entry.configure(font=self.info_font, textvariable=self.iss_var)
      self.iss_date.pack(anchor=W)

      self.action_btn_frm = tb.Frame(self.person_frm)
      
      self.action_btn = tb.Button(self.action_btn_frm, text='Assign Device', command=self.assign, bootstyle='light')
      self.action_btn.pack(expand=True, fill=BOTH) 
      
      #Changes action button funtion based on device assignment
      if self.assigned == False:
         self.action_btn.configure(text='Assign Device', command = self.assign)
      else:
         self.action_btn.configure(text='Return Device', command=self.return_dev)

      self.person_frm.pack(side=TOP, fill=tb.X, anchor=W)
      self.person_lbl_frm.pack(side=LEFT, fill=tb.Y, anchor=W)
      self.person_ent_frm.pack(side=LEFT, fill=tb.X, anchor=W)
      self.action_btn_frm.pack(side=LEFT, fill=BOTH, expand=True, anchor=W)

      #Assignment/Fact details
      self.fact_frm = tb.Frame(self)
      self.fact_lbl = tb.Label(self, text='Assignment Details', font=self.title_font, bootstyle='inverse-secondary').pack(fill=tb.X)
      
      self.fact_lbl_frm = tb.Frame(self.fact_frm, width=20)
      self.loan_lbl = tb.Label(self.fact_lbl_frm, text= 'Loaner: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.loan_sn_lbl = tb.Label(self.fact_lbl_frm, text= 'Loaner S/N: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.l_iss_date_lbl = tb.Label(self.fact_lbl_frm, text= 'Loaner Issued Date: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      
      self.fact_ent_frm = tb.Frame(self.fact_frm)
      self.loan_ent = InfoBox(self.fact_ent_frm, textvariable=self.loan_var, width=50, font=self.info_font).pack(anchor=W)
      self.loan_sn_ent = InfoBox(self.fact_ent_frm, textvariable=self.loan_sn_var, width=50, font=self.info_font).pack(anchor=W)
      self.l_iss_date_ent = InfoBox(self.fact_ent_frm, textvariable=self.l_iss_data_var, width=50, font=self.info_font).pack(anchor=W)

      self.fact_frm.pack(fill=tb.X, anchor=W)
      self.fact_lbl_frm.pack(side=LEFT, fill=tb.Y, anchor=W)
      self.fact_ent_frm.pack(side=LEFT, fill=tb.X, anchor=W)

      #Creating text fileds for damage and tech notes
      notes_lbl_frm = tb.Frame(self)
      damage_lbl = tb.Label(notes_lbl_frm, text='Repair/Damage Notes', font=self.sub_font).pack(side=LEFT, expand=True, padx=10, pady=(10, 0), anchor=W)
      tech_lbl = tb.Label(notes_lbl_frm, text='Tech Notes', font=self.sub_font).pack(side=LEFT, expand=True, padx=10, pady=(10, 0), anchor=W)
      notes_frm = tb.Frame(self)
      damage = tb.Text(notes_frm, height=20, width=60, wrap=WORD)
      tech = tb.Text(notes_frm, height=20, width=60, wrap=WORD)
      
      #Packing notes
      notes_lbl_frm.pack(fill=tb.X, pady=10)
      notes_frm.pack(fill=tb.X)
      damage.pack(side=LEFT, padx=10, pady=(0, 10), expand=True, fill=BOTH, anchor=W)
      tech.pack(side=LEFT, padx=10, pady=(0, 10), expand=True, fill=BOTH, anchor=W)

      if self.assigned == True:
         Session = sessionmaker(bind=self.controller.engine)
         self.session = Session()
         
         #Performs query to retrieve customer details from table as well as Fact table info
         self.customer_result = self.session.query(Customer, Fact).outerjoin(Fact, Fact.customer_id == Customer.customer_id).filter(Fact.device_sn == self.device.device_sn).one_or_none()
         
         #Puts returned Customer object in shorter variable name
         self.sel_cus = self.customer_result.Customer
         self.sel_fact = self.customer_result.Fact
         self.load_fact_data()
         
         self.session.close()

   def assign(self):
      
      Session = sessionmaker(bind=self.controller.engine)
      self.session = Session()

      #Creates a query to load table with users who are not issued a device and are active
      self.avl_to_assign = self.session.query(Customer).outerjoin(Fact).filter(Fact.customer_id
                                                                                == None, Customer.active==1).all()
      self.session.close()
      self.avl_list=[]
      
      #Fills row data list
      for row in self.avl_to_assign:
         self.row = (row.first_name, row.last_name, row.customer_id, row.email, row.role_, row.active)
         self.avl_list.append(self.row)

      #Creates top level window for table to search and select a user to assign the device from View page to
      self.assign_win = tb.Toplevel(title='Assign Device')
      self.assign_win.geometry('500x350')
      self.assign_win.protocol("WM_DELETE_WINDOW", self.session.close())

      self.assign_frm = tb.Frame(self.assign_win)
      self.search_lbl = tb.Label(self.assign_frm, text='Search for an Assignee', font=self.sub_font)
      self.btn = tb.Button(self.assign_frm, text='Submit', command=self.submit_assign, bootstyle='danger')

      self.coldata = ['First Name', 'Last Name', 'ID', 'email', 'role', 'active']
      self.table = Tableview(self.assign_frm,
                             bootstyle='secondary',
                             coldata=self.coldata,
                             rowdata=self.avl_list,
                             searchable=True,
                             autofit=True,
                             autoalign=True,
                             )
      self.assign_frm.pack()
      self.search_lbl.pack(pady=(5, 10))
      self.table.pack()
      self.btn.pack(pady=10)

   def submit_assign(self):
      #Retrieves selected from table
      self.assignee = self.table.get_rows(selected=True)
      #Sets all necessary fact info
      self.name_var.set(self.assignee[0].values[0] + ' ' + self.assignee[0].values[1])
      self.id_var.set(self.assignee[0].values[2])
      self.email_var.set(self.assignee[0].values[3])
      self.role_var.set(self.assignee[0].values[4])
      self.active_var.set(self.assignee[0].values[5])
      self.iss_date.entry.configure(state=NORMAL)
      self.iss_date.entry.insert(0, date.today())

      #Creates new fact object to send to db with data from viewpage and selected student/staff
      newly_assigned = Fact(self.id_var.get(),
                            self.email_var.get(),
                            self.sn_var.get(),
                            self.at_var.get(),
                            self.iss_var.get(),
                            )
      #preps the new object to be inserterd into fact table
      self.session.add(newly_assigned)
      
      #clears table from the window
      self.assign_frm.pack_forget()

      self.frame = tb.Frame(self.assign_win)
      self.sure_lbl = tb.Label(self.frame, 
                               text= f'Assign {self.sn_var.get()} to {self.name_var.get()}?',
                               font = self.sub_font)
      self.sure_btn = tb.Button(self.frame, text='Commit', command= lambda: (self.session.commit(), 
                                                                             self.assign_win.destroy()), 
                                                                             bootstyle='danger')
      self.cancel_btn = tb.Button(self.frame, text='Cancel', command= lambda: (self.session.rollback(), 
                                                                               self.frame.destroy(),
                                                                               self.assign_frm.pack()),
                                                                               bootstyle='danger')

      self.frame.pack(expand=True)
      self.sure_lbl.pack(pady=5)
      self.sure_btn.pack(pady=5)
      self.cancel_btn.pack(pady=5)

   #Returns device and puts record of the assignment into the history table
   def return_dev(self):
      Session = sessionmaker(bind=self.controller.engine)
      self.session = Session()

      #Creates object for from assignment details and defaults to current date for return date
      self.return_record = History(self.id_var.get(), self.email_var.get(), self.sn_var.get(), self.at_var.get(), self.iss_var.get(), datetime.today(), damage_notes=None)

      #Builds window for return options/info and sets window to close session if closed
      self.return_window = tb.Toplevel(title='Return Device')
      self.return_window.protocol("WM_DELETE_WINDOW", self.session.close())

      self.return_frm = tb.Frame(self.return_window)
      self.status_frm = tb.Frame(self.return_window)

      #Check button to mark the status of the device being returned as "Waiting for Tech" and to force inserting damage/repair notes
      self.check_var = StringVar()
      self.to_tech = tb.Checkbutton(self.status_frm, 
                                    text='Sending device to tech?', 
                                    variable=self.check_var, 
                                    onvalue='Waiting on Tech', 
                                    offvalue='Serviceable',
                                    bootstyle='light')
      self.dmg_notes = tb.Text(self.status_frm, height=10, width=50)

      self.return_lbl = tb.Label(self.return_window, text=f'Return {self.sn_var.get()} from {self.name_var.get()} on {date.today()}?', font=self.title_font)
      self.return_btn = tb.Button(self.return_frm, text='Commit', command=self.return_commit, bootstyle='danger')
      self.change_date_btn = tb.Button(self.return_frm, text='Change Date', command=self.change_date, bootstyle='danger')
      self.cancel_return_btn = tb.Button(self.return_frm, text='Cancel', command=self.return_window.destroy, bootstyle='danger')

      self.return_lbl.pack(pady=(10,5), padx=5)
      self.status_frm.pack(pady=5, padx=5)
      self.return_frm.pack(pady=5, padx=5)
      self.to_tech.pack(side=LEFT)
      self.dmg_notes.pack(side=LEFT, padx=5)
      self.return_btn.pack(side=LEFT, padx=5)
      self.change_date_btn.pack(side=LEFT, padx=5)
      self.cancel_return_btn.pack(side=LEFT, padx=5)


      #If status is already 'Waiting on Tech' check_var is set else is not set
      if self.stat_var.get() == 'Serviceable':
         self.check_var.set(0)
      elif self.stat_var.get() == 'Waiting on Tech':
         self.check_var.set(1)
      else:
         self.to_tech.configure(state='disabled')

   #Commits device return to history table and deletes row from fact table so device can be reassigned
   def return_commit(self):
      if self.dmg_notes.get(0.0, END) == '':
            messagebox.showwarning(message='Please insert damage/repair info')
            self.return_dev()
      else:
         if self.stat_var.get() != self.check_var.get():
            self.commit_status()

         self.fact_to_delete = self.session.query(Fact).filter_by(device_sn=self.sn_var.get()).one_or_none()
         self.session.add(self.return_record)
         self.session.flush()
         self.session.delete(self.fact_to_delete)
         self.session.commit()
         self.session.close()
         self.return_window.destroy()

   #Function to change device return date
   def change_date(self):
      self.cal = Querybox(self.return_window)
      self.return_record.returned_date = self.cal.get_date()
      self.return_lbl.configure(text=f'Return {self.sn_var.get()} from {self.name_var.get()} on {self.cal.get_date()}?')
   
   #Changes Device section label color depending on status
   def update_dev_style(self):
      if self.stat_var.get() == 'With Tech':
         self.dev_style.set('warning')
      elif self.stat_var.get() == 'Sent in for Repair':
         self.dev_style.set('warning')
      elif self.stat_var.get() == 'Waiting on Tech':
         self.dev_style.set('warning')
      elif self.stat_var.get() == 'Received From Repair':
         self.dev_style.set('warning')
      elif self.stat_var.get() == 'Unserviceable':
         self.dev_style.set('danger')
      else:
         self.dev_style.set('secondary')

   #Changes person section label color depending on status
   def update_per_style(self):
      if self.active_var.get() == 'True':
         self.per_style.set('secondary')
      else:
         self.per_style.set('danger')

   #Allows changing device status
   def update_status(self):
   
      status_win = tb.Toplevel(self)
      serv_btn = tb.Radiobutton(status_win, text='Serviceable', variable=self.stat_var, value='Serviceable')
      wait_tech_btn = tb.Radiobutton(status_win, text='Waiting on Tech', variable=self.stat_var, value='Waiting on Tech')
      tech_btn = tb.Radiobutton(status_win, text='With Tech', variable=self.stat_var, value='With Tech')
      ins_btn = tb.Radiobutton(status_win, text='Sent in for Repair', variable=self.stat_var, value='Sent in for Repair')
      recieved_btn = tb.Radiobutton(status_win, text='Received From Repair', variable=self.stat_var, value='Received From Repair')
      unserv_btn = tb.Radiobutton(status_win, text='Unserviceable', variable=self.stat_var, value='Unserviceable')

      commit_btn = tb.Button(status_win, text='Commit', command=lambda: (self.commit_status(), status_win.destroy()))

      serv_btn.pack(pady=10, padx=(5, 20), anchor=W)
      wait_tech_btn.pack(pady=10, padx=(5, 20), anchor=W)
      tech_btn.pack(pady=10, padx=(5, 20), anchor=W)
      ins_btn.pack(pady=10, padx=(5, 20), anchor=W)
      recieved_btn.pack(pady=10, padx=(5, 20), anchor=W)
      unserv_btn.pack(pady=10, padx=(5, 20), anchor=W)
      commit_btn.pack(pady=10, padx=5)

   #Commits status change to db. Works from commit button in update_status method but also called from return_commit method
   def commit_status(self):
      Session = sessionmaker(bind=self.controller.engine)
      self.session = Session()

      self.device_to_update = self.session.query(Chromebook).filter_by(device_sn=self.sn_var.get()).one_or_none()
      
      self.device_to_update.status = self.stat_var.get()
      try:
         self.session.commit()
         self.session.close()

      except Exception as e:
         messagebox.showerror(message='Unable to update status')

   def load_fact_data(self):
      self.name_var.set(self.sel_cus.first_name + ' ' + self.sel_cus.last_name)
      self.id_var.set(str(self.sel_cus.customer_id))
      self.email_var.set(self.sel_cus.email)
      self.role_var.set(self.sel_cus.role_)
      self.iss_var.set(self.sel_fact.date_issued)
      
      #Changes label colors to red if customer is not active but is still assigned the device
      #Sets boolean value for active status in label
      if self.sel_cus.active == 0:
         self.active_var.set('False')

      elif self.sel_cus.active == 1:
         self.active_var.set('True')

      #If there is a loaner this loads that data to textvariables
      if self.sel_fact.loaner == 1:
         self.loan_var.set('True')
         self.iss_var.set(str(self.sel_fact.date_issued))
         self.l_iss_data_var.set(str(self.sel_fact.loaner_issue_date))
         self.loan_sn_var.set(self.sel_fact.loaner_sn)
      else:
         self.loan_var.set('False')

class SettingsPage(tb.Frame):
   def __init__(self, parent, controller):
      tb.Frame.__init__(self, parent)  
      self.controller = controller

      heading = tb.Label(self, text= 'Settings', font=('Helvetica', 50, 'bold'))
      heading.pack(pady=(0, 10))

      self.sync_frame = tb.Labelframe(self, text = 'Sync Options')
      self.chrmbk_btn = tb.Button(self.sync_frame, text='Sync Chromebooks', command = lambda: dev_sync(self.controller.engine))
      
      
      self.sync_frame.pack(fill=tb.X)
      self.chrmbk_btn.pack()