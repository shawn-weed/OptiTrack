from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy.dialects.mssql import TEXT, BIT
import datetime
from SQLconnection import *

Base = declarative_base()

class Chromebook(Base):
    __tablename__ = 'chromebooks'

    device_sn: Mapped[str] = mapped_column('device_sn', String(50), primary_key=True, autoincrement=False)
    children: Mapped[List['Fact',]] = relationship()
    building = Column('building', String(50))
    asset_tag = Column('asset_tag', String(50))
    model = Column('model', String(50))
    status = Column('status', String(50))
    condition = Column('condition', String(50))
    con_date = Column('con_date', Date)
    damage_notes = Column('damage_notes', TEXT)

    def __init__(self, device_sn, building, asset_tag, model, status, condition, con_date, damage_notes):
        self.device_sn = device_sn
        self.building = building
        self.asset_tag = asset_tag
        self.model = model
        self.status = status
        self.condition = condition
        self.con_date = con_date
        self.damage_notes = damage_notes

    def __repr__(self):
        f'({self.device_sn}) {self.building} {self.asset_tag} {self.model} {self.status} {self.condition} {self.con_date} {self.damage_notes}'

class Customer(Base):
    __tablename__ = 'customers'

    customer_id: Mapped[int] = mapped_column('customer_id', nullable=False, primary_key=True, autoincrement=False)
    children: Mapped[List['Fact',]] = relationship()
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    role_ = Column('role_', String)
    email = Column('email', String)
    active = Column('active', BIT)

    def __init__(self, customer_id, first_name, last_name, role_, email, active):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.role_ = role_
        self.email = email
        self.active = active

    def __repr__(self):
        f'({self.customer_id}) {self.first_name} {self.last_name} {self.role_} {self.email} {self.active} {self.email}'

class Fact(Base):
    __tablename__ = 'fact'

    customer_id: Mapped[int] = mapped_column('customer_id', ForeignKey('customers.customer_id'))
    email = Column('email', String, nullable=False)
    device_sn: Mapped[str] = mapped_column('device_sn', String(50), ForeignKey('chromebooks.device_sn'), primary_key=True, autoincrement=False)
    asset_tag = Column('asset_tag', String)
    date_issued = Column('date_issued', Date)
    returned = Column('returned', BIT)
    returned_date = Column('returned_date', Date)
    loaner = Column('loaner', Integer)
    loaner_sn = Column('loaner_sn', String)
    loaner_issue_date = Column('loaner_issue_date', Date)

    def __init__(self,
                 customer_id, 
                 email, 
                 device_sn, 
                 asset_tag=None, 
                 date_issued=None, 
                 returned=None, 
                 returned_date=None, 
                 loaner=None, 
                 loaner_sn=None, 
                 loaner_issue_date=None,
                 ):
        
        self.customer_id = customer_id
        self.email = email
        self.device_sn = device_sn
        self.asset_tag = asset_tag
        self.date_issued = date_issued
        self.returned = returned
        self.returned_date = returned_date
        self.loaner = loaner
        self.loaner_sn = loaner_sn
        self.loaner_issue_date = loaner_issue_date
    
    def __repr__(self):
        f'({self.device_sn}) {self.email} {self.customer_id} {self.asset_tag} {self.date_issued} {self.returned} {self.returned_date} {self.loaner} {self.loaner_sn} {self.loaner_issue_date}'

class History(Base):
    __tablename__ = 'history'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer)
    email = Column(String)
    device_sn = Column(String)
    asset_tag = Column(String)
    date_issued = Column(Date)
    returned_date = Column(Date)
    damage_notes = Column(TEXT)

    def __init__(self, customer_id, email, deivce_sn, asset_tag, date_issued, returned_date, damage_notes):
        self.customer_id = customer_id
        self.email = email
        self.device_sn = deivce_sn
        self.asset_tag = asset_tag
        self.date_issued = date_issued
        self.returned_date = returned_date
        self.damage_notes = damage_notes

    def __repr__(self):
        f'({self.customer_id}) {self.email} {self.device_sn} {self.asset_tag} {self.date_issued} {self.returned_date} {self.damage_notes}'

class LoanerHistory(Base):
    __tablename__ = 'loaner_history'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer)
    email = Column(String)
    device_sn = Column(String)
    loaner_issue_date = Column(Date)
    returned_date = Column(Date)
    damage_notes = Column(TEXT)

    def __init__(self, customer_id, email, device_sn, loaner_issue_date, loaner_returned_date, damage_notes):
        self.customer_id = customer_id
        self.email = email
        self.device_sn = device_sn
        self.loaner_issue_date = loaner_issue_date
        self.loaner_returned_date = loaner_returned_date
        self.damage_notes = damage_notes

    def __repr__(self):
        f'({self.customer_id}) {self.email} {self.device_sn} {self.loaner_issue_date} {self.loaner_returned_date} {self.damage_notes}'