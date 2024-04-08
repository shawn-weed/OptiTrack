import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap import StringVar
from PIL import Image, ImageTk
Image.CUBIC = Image.BICUBIC
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from sqlalchemy import text, or_, not_, select, exists
from SQLconnection import *
import tkinter.ttk as ttk
from tkinter import messagebox
import pandas as pd
from sqlalchemy.orm import Session, sessionmaker
from models import Chromebook, Customer, Fact
from windowassets import InfoBox, SearchEntry
from datetime import datetime

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
                  '', 
                  row.Chromebook.status, 
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
         self.tree.autoalign_columns()
         self.tree.autofit_columns()
         self.tree.pack()

      else:
         self.tree.pack_forget()
         self.tree.build_table_data(rowdata = self.rowdata, coldata=self.coldata)
         self.tree.autoalign_columns()
         self.tree.autofit_columns()
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
      self.stat_var = StringVar(value=self.device.status)

      #Slaved variables for customer details. Only set if there is an assignment for device
      self.name_var = StringVar()
      self.id_var = StringVar()
      self.email_var = StringVar()
      self.role_var = StringVar()
      self.active_var = StringVar()

      #Slaved data for fact info. Only set if there is an assignment for device
      self.iss_var = StringVar()
      self.loan_var = StringVar()
      self.loan_sn_var = StringVar()
      self.l_iss_data_var =StringVar()

      #Creates variable to change color of person label depending on active status
      self.per_style = StringVar(value='secondary')

      # except Exception as e:
      #    messagebox.showinfo(message='Something went wrong') 

      title_font = ('default', 22, 'bold')
      sub_font = ('default', 12, 'bold')
      info_font = ('default', 12, 'normal')

      self.dev_style = StringVar()
      self.update_dev_style()
      self.stat_var.trace_add('write', lambda x, y, z: (self.update_dev_style(), self.device_lbl.configure(bootstyle = f'inverse-{self.dev_style.get()}')))

      #Device Details
      self.device_lbl = tb.Label(self, text='Device Details', font=title_font, bootstyle = f'inverse-{self.dev_style.get()}')
      self.device_lbl.pack(fill=tb.X)
      self.device_frm = tb.Frame(self,)

      self.dev_label_frame = tb.Frame(self.device_frm)
      self.sn_lbl = tb.Label(self.dev_label_frame, text= 'Device S/N: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.at_lbl = tb.Label(self.dev_label_frame, text= 'Asset Tag: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.bldg_lbl = tb.Label(self.dev_label_frame, text= 'Building: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.stat_lbl = tb.Label(self.dev_label_frame, text= 'Status: ', font=sub_font, width=20).pack(anchor=W, ipady=4)

      self.dev_ent_frame = tb.Frame(self.device_frm)
      self.sn_ent = InfoBox(self.dev_ent_frame, textvariable=self.sn_var, width=50, font=info_font,).pack(anchor=W, fill=tb.X,)
      self.at_ent = InfoBox(self.dev_ent_frame, textvariable=self.at_var, width=50, font=info_font,).pack(anchor=W, fill=tb.X,)
      self.bldg_ent = InfoBox(self.dev_ent_frame, textvariable=self.bldg_var, width=50, font=info_font,).pack(anchor=W, fill=tb.X,)
      self.stat_ent = InfoBox(self.dev_ent_frame, textvariable=self.stat_var, width=50, font=info_font,).pack(anchor=W, fill=tb.X,)

      self.dev_btn_frm = tb.Frame(self.device_frm)
      self.status_btn = tb.Button(self.dev_btn_frm, text='Update Status', command=self.update_status, bootstyle='light').pack(expand=True, fill=BOTH)
      
      self.device_frm.pack(side=TOP, fill=tb.X, expand=True, anchor=W)
      self.dev_label_frame.pack(side=LEFT, fill=tb.Y, anchor=W)
      self.dev_ent_frame.pack(side=LEFT, fill=tb.X, anchor=W)
      self.dev_btn_frm.pack(side=LEFT, fill=BOTH, expand=True, anchor=W)
      
      #Customer details
      self.person_frm = tb.Frame(self)
      self.person_lbl = tb.Label(self.person_frm, text='Assigned To', font=title_font, bootstyle = f'inverse-{self.per_style.get()}')
      self.person_lbl.pack(fill=tb.X)

      #Adds trace to active variable to change person label color
      self.active_var.trace_add('write', lambda x, y, z: (self.update_per_style(), self.person_lbl.configure(bootstyle = f'inverse-{self.per_style.get()}')))

      self.person_lbl_frm = tb.Frame(self.person_frm,)
      self.name_lbl = tb.Label(self.person_lbl_frm, text = 'Name: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.id_lbl = tb.Label(self.person_lbl_frm, text='ID: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.email_lbl = tb.Label(self.person_lbl_frm, text='Email: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.role_lbl =tb.Label(self.person_lbl_frm, text='Role: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.active_lbl = tb.Label(self.person_lbl_frm, text='Active: ', font=sub_font, width=20).pack(anchor=W, ipady=4)

      self.person_ent_frm = tb.Frame(self.person_frm)
      self.name_ent = InfoBox(self.person_ent_frm, textvariable=self.name_var, width=50, font=info_font).pack(anchor=W)
      self.id_ent = InfoBox(self.person_ent_frm, textvariable=self.id_var, width=50, font=info_font).pack(anchor=W)
      self.email_ent = InfoBox(self.person_ent_frm, textvariable=self.email_var, width=50, font=info_font).pack(anchor=W)
      self.role_ent = InfoBox(self.person_ent_frm, textvariable=self.role_var, width=50, font=info_font).pack(anchor=W)
      self.active_ent = InfoBox(self.person_ent_frm, textvariable=self.active_var, width=50, font=info_font).pack(anchor=W)
      
      self.action_btn_frm = tb.Frame(self.person_frm)
      self.action_btn = tb.Button(self.action_btn_frm, text='Assign Device', command=self.assign, bootstyle='light')
      self.action_btn.pack(expand=True, fill=BOTH) 
      
      self.person_frm.pack(side=TOP, fill=tb.X, anchor=W)
      self.person_lbl_frm.pack(side=LEFT, fill=tb.Y, anchor=W)
      self.person_ent_frm.pack(side=LEFT, fill=tb.X, anchor=W)
      self.action_btn_frm.pack(side=LEFT, fill=BOTH, expand=True, anchor=W)

      #Assignment/Fact details
      self.fact_frm = tb.Frame(self)
      self.fact_lbl = tb.Label(self, text='Assignment Details', font=title_font, bootstyle='inverse-secondary').pack(fill=tb.X)
      
      self.fact_lbl_frm = tb.Frame(self.fact_frm, width=20)
      self.iss_lbl = tb.Label(self.fact_lbl_frm, text= 'Date Issued: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.loan_lbl = tb.Label(self.fact_lbl_frm, text= 'Loaner: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.loan_sn_lbl = tb.Label(self.fact_lbl_frm, text= 'Loaner S/N: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      self.l_iss_date_lbl = tb.Label(self.fact_lbl_frm, text= 'Loaner Issued Date: ', font=sub_font, width=20).pack(anchor=W, ipady=4)
      
      self.fact_ent_frm = tb.Frame(self.fact_frm)
      self.iss_ent = InfoBox(self.fact_ent_frm, textvariable=self.iss_var, width=50, font=info_font).pack(anchor=W)
      self.loan_ent = InfoBox(self.fact_ent_frm, textvariable=self.loan_var, width=50, font=info_font).pack(anchor=W)
      self.loan_sn_ent = InfoBox(self.fact_ent_frm, textvariable=self.loan_sn_var, width=50, font=info_font).pack(anchor=W)
      self.l_iss_date_ent = InfoBox(self.fact_ent_frm, textvariable=self.l_iss_data_var, width=50, font=info_font).pack(anchor=W)

      self.fact_frm.pack(fill=tb.X, anchor=W)
      self.fact_lbl_frm.pack(side=LEFT, fill=tb.Y, anchor=W)
      self.fact_ent_frm.pack(side=LEFT, fill=tb.X, anchor=W)

      #Creating text fileds for damage and tech notes
      notes_lbl_frm = tb.Frame(self)
      damage_lbl = tb.Label(notes_lbl_frm, text='Repair/Damage Notes', font=sub_font).pack(side=LEFT, expand=True, padx=10, pady=(10, 0), anchor=W)
      tech_lbl = tb.Label(notes_lbl_frm, text='Tech Notes', font=sub_font).pack(side=LEFT, expand=True, padx=10, pady=(10, 0), anchor=W)
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

      self.avl_to_assign = self.session.query(Customer).outerjoin(Fact).filter(Fact.customer_id == None).all()
      self.avl_list=[]
      self.len_list=[]
      for row in self.avl_to_assign:
         # self.row_str = (f'{row.first_name} {row.last_name} \nID: {row.customer_id} email: {row.email}')
         # self.avl_list.append(self.row_str)
         self.row = (row.first_name, row.last_name, row.customer_id, row.email)
         self.avl_list.append(self.row)
         #Creates a list of string lengths to dynamically size the combobox to longest length
         #row_len = len(self.row_str)
         #self.len_list.append(row_len)
      print(self.avl_list)
      self.search_var = StringVar
      self.assign_win = tb.Toplevel(title='Assign Device')
      
      self.assign_win.geometry('400x400')
      self.search_frm = tb.Frame(self.assign_win)
      self.search_lbl = tb.Label(self.search_frm, text='Enter email/ID')
      self.btn = tb.Button(self.search_frm, text='Search', command=self.search, state='disabled', bootstyle='danger')
      # self.search_ent = SearchEntry(self.search_frm, self.btn, textvariable=self.search_var, width=max(self.len_list), bootstyle='secondary')
      # self.search_ent['values'] = self.avl_list

      self.coldata = ['First Name', 'Last Name', 'ID', 'email']
      self.table = Tableview(self.assign_win,
                             bootstyle='dark',
                             coldata=self.coldata,
                             rowdata=self.avl_list,
                             searchable=True,
                             autofit=True,
                             autoalign=True)
      self.table.pack()

      self.search_frm.pack()
      self.search_lbl.pack()
      # self.search_ent.pack()
      self.btn.pack(pady=10)

   def search(self):
      try:
         Session = sessionmaker(bind=self.controller.engine)
         self.session = Session()
      except Exception as e:
         messagebox.showerror(message='Unable to establish connection:\n' + str(e))
      try:   
         self.customers = self.session.query(Customer).outerjoin(Fact).filter(Fact.customer_id == None).all()

      except Exception as e:
         messagebox.showerror(message='Unable to create list:\n' + str(e))
    

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

   def update_per_style(self):
      if self.active_var.get() == 'True':
         self.per_style.set('secondary')
      else:
         self.per_style.set('danger')

   def update_status(self):
 
      Session = sessionmaker(bind=self.controller.engine)
      self.session = Session()

      self.device_to_update = self.session.query(Chromebook).filter_by(device_sn=self.device.device_sn).one_or_none()
   
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

   def commit_status(self):
      self.device_to_update.status = self.stat_var.get()
      try:
         print(self.device_to_update.device_sn, self.device_to_update.status)
         self.session.commit()
         self.session.close()

      except Exception as e:
         messagebox.showerror(message='Unable to update status')

   def load_fact_data(self):
      self.name_var.set(self.sel_cus.first_name + ' ' + self.sel_cus.last_name)
      self.id_var.set(str(self.sel_cus.customer_id))
      self.email_var.set(self.sel_cus.email)
      self.role_var.set(self.sel_cus.role_)
      
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

