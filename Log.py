import logging
import logging.handlers
import datetime
import os
import sys
import threading
import time
import calendar
from datetime import date

loggers = {}

class Log():
    global loggers
    
    def __init__(self):
        pass
    
    def getLogger(name=None):  
        if name:
            if loggers.get(name):
                return loggers.get(name)

            else:
                log = logging.getLogger(name)   
                return Log.configLog(log, name)   
        else:
            raise Exception("Precisa haver um nome para o Log")

    def configLog(log, name):

        extraField = {'dw':Log.dayWeek()}             
        log.setLevel(logging.DEBUG)
        
        h = Log.getLogHandler(name)

        log.addHandler(h)
        log = logging.LoggerAdapter(log, extraField)
        loggers[name] = log

        return log 


    def getLogHandler(name):
       
        logfile = "/var/log/Crawler/"  + Log.getDatedFolder() + name+".log"
        os.makedirs(os.path.dirname(logfile), exist_ok=True)

        h1 = logging.handlers.RotatingFileHandler(logfile, mode='w', maxBytes=104857600, backupCount=5, encoding=None, delay=False)   
        
        f = logging.Formatter("%(levelname)s [%(asctime)s] [%(dw)s] %(name)s: %(message)s")
        h1.setFormatter(f)

        return h1

    def formatError(error):
        excType, excValue, excTraceback = error

        arquivo = str(excTraceback.tb_frame.f_code.co_filename.split("/")[-1])

        strErro = 'Arquivo: [' +arquivo+"] \n" +\
                ' Linha: [' +str(excTraceback.tb_lineno)+"] \n"  +\
                ' Metodo: [' +str(excTraceback.tb_frame.f_code.co_name)+"] \n"  +\
                ' Tipo: [' +str(excType.__name__)+"] \n" +\
                ' Mensagem: [' +str(excValue)+"] \n"

        return strErro 

    
    def getDatedFolder():
        strFolder = ""
        lDate = str(datetime.datetime.now()).split(" ")[0].split('-')
        for i in lDate:
            strFolder = strFolder + i + "/"
        
        return strFolder
        
    def getLogName():
        if loggers:
            return next(iter(loggers)).split("_")[1]
        
        return "None"
    
    def dayWeek():
        myDate = date.today()
        return calendar.day_name[myDate.weekday()][0:3] 

    def getCurrentFolderData():
        try:
            global loggers
            while True:
                if loggers:
                    for name in iter(loggers):         
                        l = loggers[name]
                        count = len(l.manager.getLogger(name).handlers[:])
                        
                        for i in range(count):   
                            hdlr = l.manager.getLogger(name).handlers[i] 
                                             
                            l.manager.getLogger(name).removeHandler(hdlr)
                        
                        h = Log.getLogHandler(name)
                        
                        l.manager.getLogger(name).addHandler(h) 
                    
                time.sleep(60)

        except KeyboardInterrupt as ki:
            print(str(ki))

    def rotateFolderDay():    
        try:       
            ccs = threading.Thread(name='getCurrentFolderData', target=Log.getCurrentFolderData)
            ccs.setDaemon(True)
            ccs.start()
        except KeyboardInterrupt as ki:
            print(str(ki))

Log.rotateFolderDay()
