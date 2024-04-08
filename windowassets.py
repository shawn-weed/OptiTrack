import ttkbootstrap as tb
import tkinter as tk
from PIL import Image, ImageTk
from sqlalchemy.orm import sessionmaker
from models import *

class Header(tb.Frame):
    
    def __init__(self, parent, img_file, resizeX, resizeY, bootstyle):
        tb.Frame.__init__(self, parent, bootstyle='light')
        self.img = Image.open(img_file)
        self.img=self.img.resize((resizeX, resizeY))
        self.Tk_img = ImageTk.PhotoImage(self.img)
        
        logo=tb.Label(self, image = self.Tk_img, bootstyle=bootstyle)
        self.pack(side = 'top', fill = tb.X,)
        logo.grid(row=1, column=1)

class SearchEntry(tb.Combobox):
    def __init__(self, parent, btn, **kw):
        super().__init__(parent, **kw)
        self.parent=parent
        self.btn=btn

        text_check = self.register(self.is_valid)
        self.configure(validate='key', validatecommand=(text_check, '%P'))
    
    def is_valid(self, text):

        if  len(text) > 50:
            return False
        
        if len(text) == 0:
            self.btn.configure(text='Search', state='disabled')
            return True

        if len(text) >= 1:
            self.btn.configure(text='Search', state='normal')
            return True
            
class UsernameEntry(tb.Entry):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)

        text_check = self.register(self.is_valid)
        self.configure(validate='key', validatecommand=(text_check, '%P'))
    
    def is_valid(self, text):
        
        if  len(text) > 30:
            return False

        return True  

class PasswordEntry(tb.Entry):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw, show='\u2022')

        text_check = self.register(self.is_valid)
        self.configure(validate='key', validatecommand=(text_check, '%P'))
    
    def is_valid(text):
        
        if  len(text) > 30:
            return False
        
        return True 
    
class InfoBox(tb.Entry):
    def __init__(self, parent, *args, **kwargs):
        tb.Entry.__init__(self, parent, *args, **kwargs)

        self.bind('<Key>', lambda e: 'break')
        self.bind('<Control-c>', lambda e:self.clipboard_append(self.get()))
        self.bind('<Button-3>', self.copywindow)

    def copywindow(self, event):
        self.menu = tb.Menu(self, tearoff=0)
        self.menu.add_command(label='Copy', command=self.copy)
        self.menu.tk_popup(event.x_root, event.y_root)

    def copy(self):
        self.clipboard_append(self.get())

class AssignedMeter(tb.Meter):
    def __init__ (self, parent, engine, school=None, *args, **kwargs):
        tb.Meter.__init__(self, parent, metersize=150, padding=5, metertype='semi', textright='of' + ' ')
        self.engine = engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        total_dev = self.total_devices(school)
        total_ass = self.total_assigned(school)
        
        #Variable to contain float to change color of meter for visual represntaion of devices that are assigned
        avl_percntage = total_ass/total_dev

        if school == None:
            self.configure(amountused=total_ass, amounttotal=total_dev, subtext='Assigned', textright='of ' + str(total_dev))
        else:
            self.configure(amountused=total_ass, amounttotal=total_dev, subtext=f'{school} Assigned', textright='of ' + str(total_dev))

        if avl_percntage >= .9:
            self.configure(bootstyle='danger')
        elif avl_percntage >= .75:
            self.configure(bootstyle='warning')
        else:
            self.configure(bootstyle='success')

    def total_devices(self, school=None):
        
        if school == None:
            total_count = self.session.query(Chromebook).count()
            return total_count
        else:
            total_count = self.session.query(Chromebook).filter(Chromebook.building == school).count()
            return total_count

    def total_assigned(self, school=None):
        if school == None:
            total_assigned = self.session.query(Chromebook).outerjoin(Fact).filter(Fact.device_sn != None).count()
            return total_assigned
        else:
            total_assigned = self.session.query(Chromebook).outerjoin(Fact).filter(Fact.device_sn != None, Chromebook.building == school).count()
            return total_assigned

