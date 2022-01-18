from flask_cors import CORS
from Log import Log
from Config import Config
from flask import Flask, request,jsonify
import threading
from Crawler import Crawler
import json
import os
import time
from datetime import datetime

methods = ["stock"] 
config = Config.getConfig()

class Api():    
    def __init__(self):
        self.log = Log.getLogger("Crawler")      
    
    def storeData(self, data):
        '''Aqui eu tive que criar o cache em disco. Eu tinha tentando criar uma variavel "pool" para ser
        um cache na memória, mas não entendi porque ele não atualizava o json. Depois de um dia inteiro, 
        resolvi colocar no disco mesmo.'''
        with open('data.json', 'w') as f:
            json.dump(data, f)

    def retrieveData(self):
        try:
            '''Recupera o cache em disco.'''
            with open('data.json') as f:
                return json.load(f)
        except FileNotFoundError as fnfe:
            return {}
        
    def refreshCache(self):   
        '''Exclui o cache total após 1 hora'''     
        self.log.info("Zerando o pool...")
        threading.Timer(1*60*60, self.refreshCache).start()
        os.popen("rm -rf data.json").read()
    
    def getCurrentTimeStr(sell):
        return datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    def checkCache(self, pool):
        '''Exclui o cache após 3 min e 13 segundos'''
        lKeys = []
        for i in pool:
            dateString = pool[i][0]
            dateObject = datetime.strptime(dateString, "%Y-%m-%d, %H:%M:%S")

            dateNow = datetime.now()
            dateDiff = abs((dateNow - dateObject).seconds)
            self.log.info("Tempo do cache para a region " + i +": " + str(dateDiff) + " segundos.")
            if dateDiff > 60*3+13:
                self.log.info("Passou da hora, precisa remover.")
                lKeys.append(i)
        
        [pool.pop(k, None) for k in lKeys]
       
        if len(pool)==0:
            os.popen("rm -rf data.json").read()
        
        elif len(lKeys) > 0:
            os.popen("rm -rf data.json").read()
            self.storeData(pool)
                
    def stock(self):
        '''Endpoint para recuperação dos dados'''
        region = request.args.get('region')

        self.log.info("Recuperando dados da região " + region)

        if not region:
            msg = "Necessário passar o parametro 'region'"
            self.log.info(msg)

            return jsonify({"Error":msg}) 

        pool = self.retrieveData()    

        self.checkCache(pool)
        
    
        if region in pool:
            self.log.info("A região " + region + " já possui dados no cache")
            return jsonify(pool[region])        
        
        else:
            try:
                source = config['SERASA_CRAWLER']['source']
                crawler = Crawler(source)
                
                crawler.clickToRenew()
                crawler.clickToSelectRegion()
                
                hasRegion = crawler.selectRegion(region)
                result = None

                if hasRegion:
                    crawler.clickToPerformQuery()
                    result = crawler.extractDataTable()
                
                if not result:
                    return jsonify({"result":"Sem resultados para essa region"})

                pool.update({region:[self.getCurrentTimeStr(), result]})
                self.storeData(pool)                
                
                return jsonify(result)

            except Exception as e:
                return jsonify({"Error":str(e)})

class FlaskAppWrapper(object):

    def __init__(self, name):
        self.app = Flask(name)
        CORS(self.app)

    def run(self, config):
        self.app.run(host=config['SERASA_CRAWLER']['url'],
            debug=eval(config['SERASA_CRAWLER']['debug']),
            processes=int(config['SERASA_CRAWLER']['processes']),
            threaded=eval(config['SERASA_CRAWLER']['threaded']),
            port=int(config['SERASA_CRAWLER']['port']))

    def add_endpoint(self, endpoint=None, handler=None):
        self.app.add_url_rule(endpoint, view_func=handler, methods=['GET', 'POST'])

def init():
   
    api = Api()
    fw = FlaskAppWrapper(config['SERASA_CRAWLER']['endpoint'])

    api.refreshCache() 

    for method in methods:
        fw.add_endpoint(endpoint='/'+method, handler=eval("api."+method))

    fw.run(config)

init()
