from configparser import ConfigParser
from serverconfig import ServerConfig
import os

config = ConfigParser()

def write_file():
    config.write(open('configuration\config.ini', 'w'))

def write_host_file():
    config.write(open('configuration\hostconfig.ini', 'w'))

if not os.path.exists('configuration\config.ini'):

    config['VERSION'] = {
        'version': 'Version 1.1'
    }

    config['COLORMODE']= {
        'theme': 'darkly'
    }


    write_file()

if not os.path.exists('configuration\hostconfig.ini'):
   
   
   write_host_file()