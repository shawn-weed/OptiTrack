#SQL Connection
from sqlalchemy import create_engine
from configparser import ConfigParser

config = ConfigParser()

class MSSQLConn:
    def __init__(self, server, db, username, password):
        config.read('configuration\hostconfig.ini')
        with open('configuration\hostconfig.ini', 'r') as f:
            config.read_file(f)

        server = server
        db = db
        username = username
        pw = password
        conn_string = f'mssql+pyodbc://{username}:{pw}@{server}/{db}?driver=ODBC+Driver+17+for+SQL+Server'
        self.engine = create_engine(conn_string, pool_pre_ping=True)

class WinConn:
    def __init__(self, server, db):

        server = server
        db = db
        conn_string = f'mssql+pyodbc://{server}/{db}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'
        self.engine = create_engine(conn_string, pool_pre_ping=True)

