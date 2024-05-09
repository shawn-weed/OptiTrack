import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap import StringVar, BooleanVar
from PIL import Image, ImageTk
Image.CUBIC = Image.BICUBIC
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Querybox
from SQLconnection import *
from tkinter import messagebox
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from models import Chromebook, Customer, Fact, History
from windowassets import InfoBox
from datetime import *
from googleQuery import *

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

      #Creates variable to load new table data based on combobox selection
      self.assign_var = StringVar()
      self.assign_var.trace_add('write', self.filter_table)

      self.school_var = StringVar()
      self.school_var.trace_add('write', self.filter_table)

      #creates from for filter combobox
      filter_frm = tb.Frame(self)
      filter_frm.pack(fill=tb.X, pady=10)
   
      #Creates combobox and label to change table data
      assign_lbl = tb.Label(filter_frm, text='Filter by:', font=('Helvetca', 14))
      assign_cbx = tb.Combobox(filter_frm, textvariable=self.assign_var)
      assign_cbx['values'] = ['All',
                              'Assigned Only',
                              'Available',
                              'Loaned Out']
      assign_cbx.configure(state='readonly')
      assign_cbx.pack(side='right', padx=5)
      assign_lbl.pack(side='right', padx=5)

      #Creates combobox and label to change table data by school
      school_lbl = tb.Label(filter_frm, text='School:', font=('Helvetca', 14))
      school_cbx = tb.Combobox(filter_frm, textvariable=self.school_var)
      school_cbx['values'] = ['All',
                              'ES',
                              'MS',
                              'HS']
      school_cbx.configure(state='readonly')
      school_cbx.pack(side='right', padx=5)
      school_lbl.pack(side='right', padx=5)

      #Frame is here so when the TableView is pack_forget it will repack above the buttons
      self.tree_frm = tb.Frame(self)
      self.tree_frm.pack(expand=True, fill=BOTH)
      self.tree = Tableview(self.tree_frm, 
                            bootstyle='secondary',
                            pagesize=20, 
                            paginated=True, 
                            searchable=True, 
                            autofit=True,
                            autoalign=True, 
                            height=20,
                            stripecolor=('#3b3b3b', None),
                            )
      self.load_table()
      self.tree.pack(side=TOP, fill=BOTH)

      action_frm = tb.Frame(self)
      action_frm.pack()

      view_btn = tb.Button(action_frm, text='View', command=self.check_select_view)
      action_btn = tb.Button(action_frm, text='Action',)
      
      view_btn.pack(side='left', expand=True, padx=5, pady=5)
      action_btn.pack(side='left', expand=True, padx=5, pady=5)

      #sets default combobox selection and preps table
      school_cbx.current(0)
      assign_cbx.current(0)

   #checks the selection to change properties of View Page
   def check_select_view(self):
         if self.tree.focus() == '':
            tk.messagebox.showinfo(title=None, message="Please make a selection")
         else:
            self.selected = self.tree.get_rows(selected=True)
            #Query returns instance of Chromebook class for selected device
            #try:
            Session = sessionmaker(bind=self.controller.engine)
            session = Session()
            self.device = self.session.query(Chromebook).filter(Chromebook.device_sn == self.selected[0].values[0]).one_or_none()
            session.close()
            
            if self.selected[0].values[5] == '':
               self.assigned = False
            else:
               self.assigned = True
            viewpage = View(self.controller.container, self.controller, self.device, self.assigned)
            viewpage.grid(row=0, column=0, sticky='nsew')
            #except Exception as e:
                  #messagebox.showerror(message='Unable to retrieve device details:\n' + str(e))

   def load_table(self):
      #Queries all available devices and joins any that are assigned in Fact table
      Session = sessionmaker(bind=self.controller.engine)
      self.session = Session()
      
      self.result = self.session.query(Chromebook, Fact).outerjoin(Fact).all()
      self.session.close()

      #Sets up columns
      self.coldata =[{'text': 'Device S/N', 'stretch': True}, 
                     {'text': 'Asset Tag', 'stretch': True},
                     {'text': 'Building', 'stretch': True}, 
                     {'text': 'Status', 'stretch': True},
                     {'text': 'Condition', 'stretch': True},
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
                   row.Chromebook.condition, 
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
                  row.Chromebook.condition, 
                  '', 
                  '', 
                  '',
                  '',
                  ]
           for i in range(len(lst)):
               if lst[i] == None:
                  lst[i] = ''
         self.rowdata.append(lst)
      self.tree.build_table_data(coldata=self.coldata, rowdata=self.rowdata)
   
   #Changes table data based on combobox selection
   def filter_table(self, var, index, mode):
      self.school_data = []
      self.filtered_data = []
      
      if self.school_var.get()=='All':
         if self.assign_var.get() == 'Assigned Only':
            for row in self.rowdata:
               if row[5] != '':
                  self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Available':
            for row in self.rowdata:
               if row[5] == '':
                  if row[3] == 'ACTIVE':
                     if row[4] == 'Serviceable':
                        self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Loaned Out':
            for row in self.rowdata:
               if row[4] == 'Loaner':
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
      
      #Filters for just ES Chromebooks
      if self.school_var.get()=='ES':
         for row in self.rowdata:
            if row[2].strip() == 'ES':
               self.school_data.append(row)
         if self.assign_var.get() == 'Assigned Only':
            for row in self.school_data:
               if row[5] != '':
                  self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Available':
            for row in self.school_data:
               if row[5] == '':
                  if row[3] == 'ACTIVE':
                     if row[4] == 'Serviceable':
                        self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Loaned Out':
            for row in self.school_data:
               if row[4] == 'Loaner':
                  self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         else:
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.school_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

      #Filters for just MS Chromebooks
      if self.school_var.get()=='MS':
         for row in self.rowdata:
            if row[2].strip() == 'MS':
               self.school_data.append(row)
         if self.assign_var.get() == 'Assigned Only':
            for row in self.school_data:
               if row[5] != '':
                  self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Available':
            for row in self.school_data:
               if row[5] == '':
                  if row[3] == 'ACTIVE':
                     if row[4] == 'Serviceable':
                        self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Loaned Out':
            for row in self.school_data:
               if row[4] == 'Loaner':
                  self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         else:
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.school_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()
   

      #Filters for just HS Chromebooks
      if self.school_var.get()=='HS':
         for row in self.rowdata:
            if row[2].strip() == 'HS':
               self.school_data.append(row)
         if self.assign_var.get() == 'Assigned Only':
            for row in self.school_data:
               if row[5] != '':
                  self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Available':
            for row in self.school_data:
               if row[5] == '':
                  if row[3] == 'ACTIVE':
                     if row[4] == 'Serviceable':
                        self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         elif self.assign_var.get() == 'Loaned Out':
            for row in self.school_data:
               if row[4] == 'Loaner':
                  self.filtered_data.append(row)
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.filtered_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

         else:
            self.tree.pack_forget()
            self.tree.build_table_data(rowdata = self.school_data, coldata=self.coldata)
            self.tree.reset_table()
            self.tree.pack()

class View(ScrolledFrame):

   #The selected device from the table on search page is passed through device parameter
   def __init__(self, parent, controller, device, assigned):
      super(View, self).__init__(parent)
      self.controller = controller
      self.device = device

      self.today = date.today()
      self.date_format = '%m/%d/%Y'
      self.sp = self.controller.frames[SearchPage]

      #Slaved varaibles for selected device from search page
      self.sn_var = StringVar(value=self.device.device_sn)
      self.at_var = StringVar(value=self.device.asset_tag)
      self.bldg_var = StringVar(value=self.device.building)
      self.stat_var = StringVar(value=self.device.status)
      self.condition_var = StringVar(value=self.device.condition) #Also used for radio buttons in return_dev method
      if self.device.con_date != None:
         self.condate_var = StringVar(value=self.device.con_date)
      else:
         self.condate_var = StringVar()

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
      self.l_iss_date_var =StringVar()

      self.cus_var_list = [self.name_var,
                           self.id_var,
                           self.email_var,
                           self.role_var,
                           self.active_var,
                           self.iss_var]
      
      self.fact_var_list = [self.loan_var,
                            self.loan_sn_var,
                            self.l_iss_date_var]
      #Creates variable to change color of person label depending on active status
      self.per_style = StringVar(value='secondary')

      self.title_font = ('default', 22, 'bold')
      self.sub_font = ('default', 12, 'bold')
      self.info_font = ('default', 12, 'normal')

      #dev style is set in update_dev_style method
      self.dev_style = StringVar()
      self.update_dev_style()
      #changes label color based on device status. 
      self.condition_var.trace_add('write', lambda x, y, z: (self.update_dev_style(), 
                                                             self.return_or_assign(x, y, z), 
                                                             self.device_lbl.configure(bootstyle = f'inverse-{self.dev_style.get()}')))

      #Device Details
      self.device_lbl = tb.Label(self, text='Device Details', font=self.title_font, bootstyle = f'inverse-{self.dev_style.get()}')
      self.device_lbl.pack(fill=tb.X)
      self.device_frm = tb.Frame(self,)

      self.dev_label_frame = tb.Frame(self.device_frm)
      self.sn_lbl = tb.Label(self.dev_label_frame, text= 'Device S/N: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.at_lbl = tb.Label(self.dev_label_frame, text= 'Asset Tag: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.bldg_lbl = tb.Label(self.dev_label_frame, text= 'Building: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.stat_lbl = tb.Label(self.dev_label_frame, text='Status: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.condition_lbl = tb.Label(self.dev_label_frame, text= 'Condition: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)
      self.condate_lbl = tb.Label(self.dev_label_frame, text= 'Condition Date: ', font=self.sub_font, width=20).pack(anchor=W, ipady=4)

      self.dev_ent_frame = tb.Frame(self.device_frm)
      self.sn_ent = InfoBox(self.dev_ent_frame, textvariable=self.sn_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.at_ent = InfoBox(self.dev_ent_frame, textvariable=self.at_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.bldg_ent = InfoBox(self.dev_ent_frame, textvariable=self.bldg_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.stat_ent = InfoBox(self.dev_ent_frame, textvariable=self.stat_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.condition_ent = InfoBox(self.dev_ent_frame, textvariable=self.condition_var, width=50, font=self.info_font,).pack(anchor=W, fill=tb.X,)
      self.con_date = tb.DateEntry(self.dev_ent_frame, bootstyle='secondary', dateformat=self.date_format, width=47, startdate=None)
      self.con_date.configure(state=READONLY)
      self.con_date.button.configure(state='disabled')
      self.con_date.entry.configure(font=self.info_font, textvariable=self.condate_var)
      self.con_date.pack(anchor=W)

      self.dev_btn_frm = tb.Frame(self.device_frm)
      self.condition_btn = tb.Button(self.dev_btn_frm, text='Update Condition', command=self.update_condition, bootstyle='light')
      self.condition_btn.pack(expand=True, fill=BOTH)

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
      self.iss_date = tb.DateEntry(self.person_ent_frm, bootstyle='secondary', dateformat=self.date_format, width=47, startdate=None)
      self.iss_date.entry.delete(0, END)
      self.iss_date.button.configure(state='disabled')
      self.iss_date.configure(state=READONLY)
      self.iss_date.entry.configure(font=self.info_font, textvariable=self.iss_var)
      self.iss_date.pack(anchor=W)

      self.action_btn_frm = tb.Frame(self.person_frm)
      
      self.assigned = BooleanVar()
      self.action_btn = tb.Button(self.action_btn_frm, text='Assign Device', command=self.assign, bootstyle='light')
      self.action_btn.pack(expand=True, fill=BOTH) 

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
      self.l_iss_date_ent = InfoBox(self.fact_ent_frm, textvariable=self.l_iss_date_var, width=50, font=self.info_font).pack(anchor=W)

      self.fact_frm.pack(fill=tb.X, anchor=W)
      self.fact_lbl_frm.pack(side=LEFT, fill=tb.Y, anchor=W)
      self.fact_ent_frm.pack(side=LEFT, fill=tb.X, anchor=W)

      self.loan_frm = tb.Frame(self.fact_frm)
      self.loan_frm.pack(side=LEFT, fill=BOTH, expand=True, anchor=W)
      self.loan_btn = tb.Button(self.loan_frm, text='Assign Loaner', 
                                command=self.assign_loaner, 
                                bootstyle='light')
      self.loan_var.trace_add('write', self.ln_return_or_assign)
      self.loan_btn.pack(expand=True, fill=BOTH)

      #Adds trace to assigned variable. Must be after loan_btn declaration as it changes state of loan_btn based on assigned variable
      self.assigned.trace_add('write', self.return_or_assign)
      self.assigned.set(assigned)

      #Creating text fileds for damage and tech notes
      notes_lbl_frm = tb.Frame(self)
      damage_lbl = tb.Label(notes_lbl_frm, text='Repair/Damage Notes', font=self.sub_font).pack(side=LEFT, expand=True, padx=10, pady=(10, 0), anchor=W)
      notes_frm = tb.Frame(self)
      self.damage = tb.Text(notes_frm, height=20, width=60, wrap=WORD)
      if self.device.damage_notes != None:
         self.damage.insert(1.0, self.device.damage_notes)
      #Packing notes
      notes_lbl_frm.pack(fill=tb.X, pady=10)
      notes_frm.pack(fill=tb.X)
      self.damage.pack(side=LEFT, padx=10, pady=(0, 10), expand=True, fill=BOTH, anchor=W)

      if self.assigned.get() == True:
         Session = sessionmaker(bind=self.controller.engine)
         session = Session()
         
         #Performs query to retrieve customer details from table as well as Fact table info
         self.customer_result = session.query(Customer, Fact).outerjoin(Fact, Fact.customer_id == Customer.customer_id).filter(Fact.device_sn == self.device.device_sn).one_or_none()
         
         #Puts returned Customer object in shorter variable name
         self.sel_cus = self.customer_result.Customer
         self.sel_fact = self.customer_result.Fact
         self.load_fact_data()
         
         session.close()
      else:
         self.loan_btn.configure(state='disabled')

      #Run this to ensure all entries are set properly
      self.return_or_assign()

   def return_or_assign(self, var=None, index=None, mode=None):
      #Changes action button funtion based on device assignment
      if self.stat_var.get() != 'ACTIVE':
         self.action_btn.configure(state='disabled')
      elif self.assigned.get() == False:
         if self.stat_var.get() == 'ACTIVE':
            if self.condition_var.get() == 'Serviceable':
               self.action_btn.configure(text='Assign Device', command = self.assign)
            else:
               self.action_btn.configure(state='disabled')
      elif self.assigned.get() == False:
         if self.stat_var.get() != 'ACTIVE':
            self.action_btn.configure(state='disabled')
      elif self.assigned.get() == True:
         if self.loan_var.get() == 'True':
            self.action_btn.configure(state='disabled')
         elif self.loan_var.get() == '':
            self.action_btn.configure(text='Return Device', command=self.return_loaner)
            self.loan_btn.configure(state='normal')
         else:
            self.action_btn.configure(text='Return Device', command=self.return_loaner)
            self.loan_btn.configure(state='normal')
      else:
         self.action_btn.configure(text='Disabled', state='disabled')
         

      #Changes state of self.action_btn based on device condition. Allows returning device if already assigned and condition is changed
      if self.condition_var.get() == 'Loaner':
         self.action_btn.configure(state='disabled')
         self.condition_btn.configure(state='disabled')
   
   def ln_return_or_assign(self, var=None, index=None, mode=None):
      #Changes loaner button funtion based on device assignment
      
      if self.loan_var.get() == 'False':
         self.loan_btn.configure(text='Assign Loaner', command=self.assign_loaner)
      else:
         self.loan_btn.configure(text='Return Loaner', command=self.return_loaner)

   def assign(self):
      
      Session = sessionmaker(bind=self.controller.engine)
      self.session = Session()

      #Creates a query to load table with users who are not issued a device and are active students
      self.stu_to_assign = self.session.query(Customer).outerjoin(Fact).filter(Fact.customer_id == None, 
                                                                               Customer.active==1, 
                                                                               Customer.role_ == 'student').all()
      
      #Creates query load table with active faculty
      self.fac_to_assign = self.session.query(Customer).outerjoin(Fact).filter(Customer.active==1, 
                                                                               Customer.role_ == 'faculty').all()

      self.session.close()
      #Fills row data list
      self.stu_list = []
      for row in self.stu_to_assign:
         self.row = (row.first_name, row.last_name, row.customer_id, row.email, row.role_, row.active)
         self.stu_list.append(self.row)

      self.fac_list = []
      for row in self.fac_to_assign:
         self.row = (row.first_name, row.last_name, row.customer_id, row.email, row.role_, row.active)
         self.fac_list.append(self.row)

      #Creates top level window for table to search and select a user to assign the device from View page to
      self.assign_win = tb.Toplevel(title='Assign Device')
      self.assign_win.protocol("WM_DELETE_WINDOW", self.session.close())
      self.assign_win.grab_set()

      self.assign_frm = tb.Frame(self.assign_win)
      self.search_lbl = tb.Label(self.assign_frm, text='Search for an Assignee', font=self.sub_font)
      self.btn = tb.Button(self.assign_frm, text='Submit', command=self.submit_assign, bootstyle='danger')
      
      self.radio_var = StringVar()
      self.custype_frm = tb.Frame(self.assign_frm)
      self.stu_radio = tb.Radiobutton(self.custype_frm, text='Assign to Student', variable=self.radio_var, value='Student', command=self.load_ass_table)
      self.fac_radio = tb.Radiobutton(self.custype_frm, text='Assign to Faculty', variable=self.radio_var, value='Faculty', command=self.load_ass_table)

      self.coldata = ['First Name', 'Last Name', 'ID', 'email', 'role', 'active']
      self.table = Tableview(self.assign_frm,
                             bootstyle='secondary',
                             coldata=self.coldata,
                             searchable=True,
                             autofit=True,
                             autoalign=True,
                             )
      self.assign_frm.pack()
      self.search_lbl.pack(pady=(5, 10))
      self.custype_frm.pack()
      self.stu_radio.pack(side=LEFT, pady=5)
      self.fac_radio.pack(side=LEFT, pady=5)
      self.table.pack(padx=5, pady=5)
      self.btn.pack(pady=10)

   def load_ass_table(self):
      if self.radio_var.get() == 'Student':
         self.table.build_table_data(rowdata=self.stu_list, coldata=self.coldata)
         self.table.reset_table()
      elif self.radio_var.get() == 'Faculty':
         self.table.build_table_data(rowdata=self.fac_list, coldata=self.coldata)
         self.table.reset_table()

   def submit_assign(self):
      #Retrieves selected from table
      self.assignee = self.table.get_rows(selected=True)
      self.name_var.set(self.assignee[0].values[0] + ' ' + self.assignee[0].values[1])
      self.id_var.set(self.assignee[0].values[2])
      self.email_var.set(self.assignee[0].values[3])
      self.role_var.set(self.assignee[0].values[4])
      if self.assignee[0].values[5] == True:
         self.active_var.set('True')
      elif self.assignee[0].values[5 == False]:
         self.active_var.set('False')
      self.iss_var.set(self.today.strftime(self.date_format))
      self.loan_var.set('False')

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
                                                                             self.assign_win.destroy(),
                                                                             self.sp.load_table(),
                                                                             self.sp.tree.reset_table(),
                                                                             self.assigned.set(True),
                                                                             ),
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

      self.check_var = StringVar()
      self.check_var.trace_add('write', self.notes_chg)

      #Creates object for from assignment details and defaults to current date for return date
      self.return_record = History(self.id_var.get(), self.email_var.get(), self.sn_var.get(), self.at_var.get(), self.iss_var.get(), str(self.today.strftime(self.date_format)), damage_notes=self.damage.get(1.0, END))
      self.to_update = self.session.query(Chromebook).filter_by(device_sn=self.sn_var.get()).one_or_none
      #Builds window for return options/info and sets window to close session if closed
      self.return_window = tb.Toplevel(title='Return Device')
      self.return_window.protocol("WM_DELETE_WINDOW", self.session.close())
      self.return_window.grab_set()

      self.return_frm = tb.Frame(self.return_window)
      self.condition_frm = tb.Frame(self.return_window)

      #Check button to mark the condition of the device being returned as "Waiting for Tech" and to force inserting damage/repair notes
      self.to_tech = tb.Checkbutton(self.condition_frm, 
                                    text='Sending device to tech?', 
                                    variable=self.check_var, 
                                    onvalue='Waiting on Tech', 
                                    offvalue='Serviceable',
                                    bootstyle='light')
      self.dmg_notes = tb.Text(self.condition_frm, height=10, width=50)

      self.return_lbl = tb.Label(self.return_window, text=f'Return {self.sn_var.get()} from {self.name_var.get()} on {self.today.strftime(self.date_format)}?', 
                                 font=self.title_font)
      self.return_btn = tb.Button(self.return_frm, text='Commit', 
                                  command=self.return_commit, 
                                  bootstyle='danger')
      self.change_date_btn = tb.Button(self.return_frm, 
                                       text='Change Date', 
                                       command=self.change_date(self.return_lbl, self.return_record), 
                                       bootstyle='danger')
      self.cancel_return_btn = tb.Button(self.return_frm, 
                                         text='Cancel', 
                                         command=self.return_window.destroy, 
                                         bootstyle='danger')

      self.return_lbl.pack(pady=(10,5), padx=5)
      self.condition_frm.pack(pady=5, padx=5)
      self.return_frm.pack(pady=5, padx=5)
      self.to_tech.pack(side=LEFT)
      self.dmg_notes.pack(side=LEFT, padx=5)
      self.return_btn.pack(side=LEFT, padx=5)
      self.change_date_btn.pack(side=LEFT, padx=5)
      self.cancel_return_btn.pack(side=LEFT, padx=5)


      #If status is already 'Waiting on Tech' check_var is set else is not set
      if self.condition_var.get() == 'Serviceable':
         self.check_var.set(0)
      elif self.condition_var.get() == 'Waiting on Tech':
         self.check_var.set(1)
      else:
         self.to_tech.configure(state='normal')

   #Commits device return to history table and deletes row from fact table so device can be reassigned
   def return_commit(self):
      #If sending to tech was checked forces input of reason why
      if self.condition_var.get() == 'Waiting on Tech':  
         if self.dmg_notes.get(0.0, END) == '':
            messagebox.showwarning(message='Please insert damage/repair info')
            self.return_dev()
      #Ensures condition is correct in db from user changes in software
      else:
         if self.condition_var.get() != self.check_var.get():
            self.commit_condition()
         #Adds data from device assignment to history table. Then deletes row from fact table so the device can be reassigned but a record is kept
         try:
            self.fact_to_delete = self.session.query(Fact).filter_by(device_sn=self.sn_var.get()).one_or_none()
            self.session.add(self.return_record)
            self.return_record = self.dmg_notes.get(1.0, END)
            self.to_update.damage_notes = self.dmg_notes.get(1.0, END)
            self.session.flush()
            self.session.delete(self.fact_to_delete)
            self.session.commit()
            #Queries fact table against sn to verify the record is removed from the fact table.
            try:
               self.check = self.session.query(Fact).filter_by(device_sn=self.sn_var.get()).one_or_none()
               #Clears entry fields that contain data from fact table
               if self.check == None:
                  for item in self.cus_var_list:
                     item.set('')
                  self.loan_var.set('')
               else:
                  messagebox.showerror(message='Device still assigned!\nPlease retry returning the device')
            except:
               messagebox.showwarning(message='Unable to verify return\nPlease verify by checking search table')
            
         except Exception as e:
            messagebox.showerror(message='Unable to commit return:\nError: ' + str(e))
            
         self.return_window.destroy()
         self.assigned.set(False)
         self.sp.load_table()
         self.sp.tree.reset_table()
         
   #Function to change device return date
   def change_date(self, lbl, var):
      self.cal = Querybox()
      var.returned_date = self.cal.get_date()
      lbl.configure(text=f'Return {self.sn_var.get()} from {self.name_var.get()} on {self.cal.get_date()}?')
   
   #Changes Device section label color depending on condition
   def update_dev_style(self):
      if self.condition_var.get() == 'With Tech':
         self.dev_style.set('warning')
      elif self.condition_var.get() == 'Sent in for Repair':
         self.dev_style.set('warning')
      elif self.condition_var.get() == 'Waiting on Tech':
         self.dev_style.set('warning')
      elif self.condition_var.get() == 'Received From Repair':
         self.dev_style.set('warning')
      elif self.condition_var.get() == 'Unserviceable':
         self.dev_style.set('danger')
      else:
         self.dev_style.set('secondary')

   #Changes person section label color depending on status
   def update_per_style(self):
      if self.active_var.get() == 'False':
         self.per_style.set('danger')
      else:
         self.per_style.set('secondary')

   #Allows changing device condition
   def update_condition(self):
   
      self.condition_win = tb.Toplevel(self)
      self.condition_win.protocol('WM_DELETE_WINDOW', self.negate_x)
      self.condition_win.grab_set()

      serv_btn = tb.Radiobutton(self.condition_win, text='Serviceable', variable=self.condition_var, value='Serviceable')
      wait_tech_btn = tb.Radiobutton(self.condition_win, text='Waiting on Tech', variable=self.condition_var, value='Waiting on Tech')
      tech_btn = tb.Radiobutton(self.condition_win, text='With Tech', variable=self.condition_var, value='With Tech')
      ins_btn = tb.Radiobutton(self.condition_win, text='Sent in for Repair', variable=self.condition_var, value='Sent in for Repair')
      recieved_btn = tb.Radiobutton(self.condition_win, text='Received From Repair', variable=self.condition_var, value='Received From Repair')
      unserv_btn = tb.Radiobutton(self.condition_win, text='Unserviceable', variable=self.condition_var, value='Unserviceable')


      date_ent = tb.DateEntry(self.condition_win, bootstyle='secondary', dateformat=self.date_format, startdate=date.today())
      date_ent.entry.configure(textvariable=self.condate_var)
      self.condate_var.set(self.today.strftime(self.date_format))
      
      btn_frm = tb.Frame(self.condition_win)
      commit_btn = tb.Button(btn_frm, text='Commit', 
                             command=self.commit_condition, 
                             bootstyle='danger', width=10)
      cancel_btn = tb.Button(btn_frm, text='Cancel', 
                             command=self.negate_x,
                             bootstyle='danger', 
                             width=10)

      serv_btn.pack(pady=10, padx=(5, 20), anchor=W)
      wait_tech_btn.pack(pady=10, padx=(5, 20), anchor=W)
      tech_btn.pack(pady=10, padx=(5, 20), anchor=W)
      ins_btn.pack(pady=10, padx=(5, 20), anchor=W)
      recieved_btn.pack(pady=10, padx=(5, 20), anchor=W)
      unserv_btn.pack(pady=10, padx=(5, 20), anchor=W)
      date_ent.pack(pady=10, padx=(5,20), anchor=W)
      btn_frm.pack(pady=10, padx=5)
      commit_btn.pack(padx=5, side=LEFT)
      cancel_btn.pack(padx=5, side=LEFT)

   #Commits status change to db. Works from commit button in update_status method but also called from return_commit method
   def commit_condition(self):
      condate = self.condate_var.get()
      if datetime.datetime.strptime(condate, self.date_format).date() > self.today:
         messagebox.showinfo(message=f'Date can not be after today {self.today.strftime(self.date_format)}')
      else:
         self.condition_win.destroy()
         Session = sessionmaker(bind=self.controller.engine)
         self.session = Session()

         self.device_to_update = self.session.query(Chromebook).filter_by(device_sn=self.sn_var.get()).one_or_none()
         
         self.device_to_update.condition = self.condition_var.get()
         self.device_to_update.con_date = self.condate_var.get()

         try:
            self.session.commit()
            self.session.close()
            self.sp.load_table()
            self.sp.tree.reset_table()

         except Exception as e:
            messagebox.showerror(message='Unable to update condition:\n' + str(e))

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
         self.l_iss_date_var.set(str(self.sel_fact.loaner_issue_date))
         self.loan_sn_var.set(self.sel_fact.loaner_sn)
         self.loan_btn.configure(text='Return Loaner', state='normal', command=self.return_loaner)
      else:
         self.loan_var.set('False')
   
   #Starts assignment of loaner
   def assign_loaner(self):
      Session = sessionmaker(bind=self.controller.engine)
      self.loansession = Session()

      self.loan_result = self.loansession.query(Chromebook).outerjoin(Fact).filter(and_(Chromebook.condition=='Serviceable',
                                                                                   Chromebook.status=='ACTIVE'),
                                                                                   Fact.device_sn == None).all()
      
      self.avl_loan = []
      for row in self.loan_result:
         row = (row.device_sn, row.building, row.asset_tag, row.condition)
         self.avl_loan.append(row)

      self.loan_win = tb.Toplevel(title='Loan Device')
      self.loan_frm = tb.Frame(self.loan_win)
      self.assign_loan_lbl = tb.Label(self.loan_frm, text='Select a Device', font=self.title_font)
      self.loan_win.grab_set()

      self.loancoldata = ['Device S/N', 'Building', 'Asset Tag', 'Condition']
      self.loan_table = Tableview(self.loan_frm,
                             bootstyle='secondary',
                             coldata=self.loancoldata,
                             rowdata=self.avl_loan,
                             searchable=True,
                             autofit=True,
                             autoalign=True,
                             )
      self.loan_assign_btn = tb.Button(self.loan_frm, text='Assign Loaner', command=self.commit_loaner, bootstyle='danger')
      
      #pack all
      self.loan_frm.pack(expand=True)
      self.assign_loan_lbl.pack(pady=(5,10))
      self.loan_table.pack(padx=5)
      self.loan_assign_btn.pack(pady=(10,5))
   
   def commit_loaner(self):
      #Set variables for View Page
      self.loan_dev = self.loan_table.get_rows(selected=True)
      self.loan_sn_var.set(self.loan_dev[0].values[0])
      self.l_iss_date_var.set(self.today.strftime(self.date_format))
      print(self.loan_sn_var.get())
      #preps the new object to be inserterd into fact table
      try:
         self.fact_update = self.loansession.query(Fact).filter_by(device_sn = self.sn_var.get()).one_or_none()
         self.chrmbk_update = self.loansession.query(Chromebook).filter_by(device_sn = self.loan_sn_var.get()).one_or_none()
      except Exception as e:
         messagebox.showerror(message='Cannot connect to database. Please try again\nError: ' + str(e))

      self.fact_update.loaner = 1
      self.fact_update.loaner_sn = self.loan_sn_var.get()
      self.fact_update.loaner_issue_date = self.l_iss_date_var.get()

      self.chrmbk_update.condition = 'Loaner'
      self.loan_frm.pack_forget()
      
      self.loan_commit_frm = tb.Frame(self.loan_win)
      self.loan_commit_lbl = tb.Label(self.loan_commit_frm, text=f'Assign {self.loan_sn_var.get()} to {self.name_var.get()}?', font=self.title_font)
      self.loan_commit_btn = tb.Button(self.loan_commit_frm, text='Commit', command= lambda: (self.loansession.commit(), 
                                                                             self.loan_win.destroy(),
                                                                             self.sp.load_table(),
                                                                             self.sp.tree.reset_table(),
                                                                             self.loan_var.set('True'),
                                                                             ),
                                                                             bootstyle='danger')
      self.loan_cancel_btn = tb.Button(self.loan_commit_frm, text='Cancel', command= lambda: (self.loansession.rollback(), 
                                                                               self.loan_commit_frm.destroy(),
                                                                               self.loan_frm.pack(),
                                                                               self.loan_sn_var.set(''),
                                                                               self.l_iss_date_var.set('')),
                                                                               bootstyle='danger')

      self.loan_commit_frm.pack(expand=True)
      self.loan_commit_lbl.pack(pady=5)
      self.loan_commit_btn.pack(pady=5)
      self.loan_cancel_btn.pack(pady=5)

   def return_loaner(self):
      Session = sessionmaker(bind=self.controller.engine)
      self.loan_rtnsession = Session()

      self.loan_check_var = StringVar()
      self.loan_check_var.trace_add('write', self.loan_notes_chg)

      #Creates object for from assignment details and defaults to current date for return date
      self.loan_return_record = LoanerHistory(self.id_var.get(), self.email_var.get(), self.loan_sn_var.get(), self.l_iss_date_var.get(), str(self.today.strftime(self.date_format)), damage_notes=None)

      #Builds window for return options/info and sets window to close session if closed
      self.loan_return_window = tb.Toplevel(title='Return Loaner')
      self.loan_return_window.protocol("WM_DELETE_WINDOW", self.loan_rtnsession.close())
      self.loan_return_window.grab_set()

      self.loan_return_frm = tb.Frame(self.loan_return_window)
      self.loan_condition_frm = tb.Frame(self.loan_return_window)

      #Check button to mark the condition of the device being returned as "Waiting for Tech" and to force inserting damage/repair notes
      self.loan_check_var = StringVar()
      self.loan_check_var.trace_add('write', self.loan_notes_chg)
      self.loan_to_tech = tb.Checkbutton(self.loan_condition_frm, 
                                    text='Sending device to tech?', 
                                    variable=self.loan_check_var, 
                                    onvalue='Waiting on Tech', 
                                    offvalue='Serviceable',
                                    bootstyle='light')
      self.loan_dmg_notes = tb.Text(self.loan_condition_frm, height=10, width=50)

      self.loan_return_lbl = tb.Label(self.loan_return_window, text=f'Return {self.loan_sn_var.get()} from {self.name_var.get()} on {self.today.strftime(self.date_format)}?', 
                                 font=self.title_font)
      self.loan_return_btn = tb.Button(self.loan_return_frm, text='Commit', 
                                  command=self.return_loaner_commit, 
                                  bootstyle='danger')
      self.loan_change_date_btn = tb.Button(self.loan_return_frm, 
                                       text='Change Date', 
                                       command=lambda: self.change_date(self.loan_return_lbl, self.loan_return_record), 
                                       bootstyle='danger')
      self.loan_cancel_return_btn = tb.Button(self.loan_return_frm, 
                                         text='Cancel', 
                                         command=self.loan_return_window.destroy, 
                                         bootstyle='danger')

      self.loan_return_lbl.pack(pady=(10,5), padx=5)
      self.loan_condition_frm.pack(pady=5, padx=5)
      self.loan_return_frm.pack(pady=5, padx=5)
      self.loan_to_tech.pack(side=LEFT)
      self.loan_dmg_notes.pack(side=LEFT, padx=5)
      self.loan_return_btn.pack(side=LEFT, padx=5)
      self.loan_change_date_btn.pack(side=LEFT, padx=5)
      self.loan_cancel_return_btn.pack(side=LEFT, padx=5)

   def return_loaner_commit(self):
         #Adds data from device assignment to loaner history table. Then removes loaner info from fact table and sets condition of loaner device
         try:
            self.fact_to_update = self.loan_rtnsession.query(Fact).filter_by(device_sn=self.sn_var.get()).one_or_none()
            #Queries loaner in chromebook table to change condition from loaner
            self.chrmbk_to_update = self.loan_rtnsession.query(Chromebook).filter_by(device_sn=self.loan_sn_var.get()).one_or_none()
            self.chrmbk_to_update.condition = self.loan_check_var.get()
            self.chrmbk_to_update.con_date = self.today
            self.chrmbk_to_update.damage_notes = self.loan_dmg_notes.get(1.0, END)
            self.loan_return_record.damage_notes = self.loan_dmg_notes.get(1.0, END)
            self.loan_rtnsession.add(self.loan_return_record)
            self.loan_rtnsession.flush()
            self.fact_to_update.loaner = False
            self.fact_to_update.loaner_sn = None
            self.fact_to_update.loaner_issue_date = None
            self.loan_rtnsession.commit()
            #Queries fact table against sn to verify the record is removed from the fact table.
            try:
               self.check = self.loan_rtnsession.query(Fact).filter_by(device_sn=self.sn_var.get()).one_or_none()
               #Clears entry fields that contain data from fact table
               if self.check.loaner_sn == None:
                  for item in self.fact_var_list:
                     item.set('')
                  self.loan_var.set('')
                  self.loan_rtnsession.close()
               else:
                  messagebox.showerror(message='Device still assigned!\nPlease retry returning the device')
                  self.loan_rtnsession.rollback()
                  self.loan_rtnsession.close()
            except Exception as e:
               messagebox.showwarning(message='Unable to verify return\nPlease verify by checking search table\nError: ' + str(e))
            
         except Exception as e:
            messagebox.showerror(message='Unable to commit return\nError: ' + str(e))
            
         self.loan_return_window.destroy()
         self.sp.load_table()
         self.sp.tree.reset_table()

   def notes_chg(self, var, index, mode):
      if self.check_var.get() == 'Waiting on Tech':
         self.dmg_notes.configure(state='normal')
      else:
         self.dmg_notes.configure(state='disabled')

   def loan_notes_chg(self, var, index, mode):
      if self.loan_check_var.get() == 'Waiting on Tech':
         self.loan_dmg_notes.configure(state='normal')
      else:
         self.loan_dmg_notes.configure(state='disabled')

#Comes in to reset condition variables to what they were if user cancels or closes out the condition update window
   def negate_x(self):
      Session = sessionmaker(bind=self.controller.engine)
      session = Session()
      chrmbk_status = session.query(Chromebook).filter_by(device_sn=self.sn_var.get()).one_or_none()
      try:
         if chrmbk_status != None:
            self.condate_var.set(chrmbk_status.con_date)
            self.condition_var.set(chrmbk_status.condition)
            self.condition_win.destroy()
      except Exception as e:
         messagebox.showerror(message='Unable update Chromebook condition. Please reload the page\nError: ' + str(e))
         self.condition_win.destroy()
         self.controller.show_frame[SearchPage]

class SettingsPage(tb.Frame):
   def __init__(self, parent, controller):
      tb.Frame.__init__(self, parent)  
      self.controller = controller
      self.sp = self.controller.frames[SearchPage]

      heading = tb.Label(self, text= 'Settings', font=('Helvetica', 50, 'bold'))
      heading.pack(pady=(0, 10))

      self.sync_frame = tb.Labelframe(self, text = 'Sync Options')
      self.chrmbk_btn = tb.Button(self.sync_frame, text='Sync Chromebooks', command = self.sync_chrmbks, bootstyle='danger')
      self.user_btn = tb.Button(self.sync_frame, text='Sync Users', bootstyle='danger')
      
      self.sync_frame.pack(fill=tb.X)
      self.chrmbk_btn.pack(side=LEFT, expand=True, padx=5, pady=5)
      #self.user_btn.pack(side=LEFT, expand=True, padx=5)

   def sync_chrmbks(self):
      self.sync = Sync(self.controller.engine)
      self.sp.load_table()
      self.sp.tree.reset_table()