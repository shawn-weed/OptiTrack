from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy.dialects.mssql import TEXT, BIT
import datetime
from SQLconnection import *

Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'

#     uid = Column(Integer, primary_key=True)
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     password = Column(String(100), unique=True, nullable=False)
#     first_login = Column(String(1), nullable=False, default=0)
#     sec_question1 = Column(String(50))
#     sec_question2 = Column(String(50))
#     created_at = Column(DateTime, default=datetime.datetime.now)

#     def __init__(self, id, username, email, password):
#         self.id = id
#         self.username = username
#         self.email = email
#         self.password = password
    
#     def __repr__(self):
#         f'({self.id}) {self.username} {self.email} {self.password}'

class Chromebook(Base):
    __tablename__ = 'chromebooks'

    device_sn: Mapped[str] = mapped_column('device_sn', String(50), primary_key=True, autoincrement=False)
    children: Mapped[List['Fact',]] = relationship()
    building = Column('building', String(50))
    asset_tag = Column('asset_tag', String(50))
    model = Column('model', String(50))
    status = Column('status', String(50))

    def __init__(self, device_sn, building, asset_tag, model, status):
        self.device_sn = device_sn
        self.building = building
        self.asset_tag = asset_tag
        self.model = model
        self.status = status

    def __repr__(self):
        f'({self.device_sn}) {self.building} {self.asset_tag} {self.model} {self.status}'

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
    date_issued = Column('date_issued', DateTime)
    returned = Column('returned', BIT)
    returned_date = Column('returned_date', DateTime)
    loaner = Column('loaner', Integer)
    loaner_sn = Column('loaner_sn', String)
    loaner_issue_date = Column('loaner_issue_date', DateTime)
    loaner_returned_date = Column('loaner_returned_date', DateTime)
    damage_notes = Column('damage_notes', TEXT)
    tech_notes = Column('tech_notes', TEXT)

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
                 loaner_returned_date=None, 
                 damage_notes=None, 
                 tech_notes=None, 
                 to_tech=None):
        
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
        self.loaner_returned_date = loaner_returned_date
        self.damage_notes = damage_notes
        self.tech_notes = tech_notes
        self.to_tech = to_tech
    
    def __repr__(self):
        f'({self.device_sn}) {self.email} {self.customer_id} {self.asset_tag} {self.date_issued} {self.returned} {self.returned_date} {self.loaner} {self.loaner_sn} {self.loaner_issue_date} {self.loaner_returned_date} {self.damage_notes} {self.tech_notes} {self.to_tech}'

class History(Base):
    __tablename__ = 'history'

    customer_id = Column(Integer, primary_key=True, autoincrement=False)
    email = Column(String)
    device_sn = Column(String)
    asset_tag = Column(String)
    date_issued = Column(DateTime)
    returned_date = Column(DateTime)
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
