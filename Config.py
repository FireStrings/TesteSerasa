import configparser
import os 
import sys
import os.path
from Log import Log

class Config():
    
    def __init__(self):
        pass
        
    def getConfig():        
        try:           
            config = configparser.ConfigParser()
            config.sections()

            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            config.read(root_dir + "/TesteSerasa/dev.conf")            

            return config

        except:
            raise Exception(Log.formatError(sys.exc_info()))

    