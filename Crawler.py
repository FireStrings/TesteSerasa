from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import math
import sys
from Log import Log

class Crawler():
    def __init__(self, source):
        self.log = Log.getLogger("Crawler")
        self.firefox = None
        self.loadSource(source)   
        self.dFinal = {}

    def loadSource(self, source):
        try:
            self.log.info("Configurando o source")
            self.firefox = webdriver.Firefox()
            self.firefox.get(source)
            self.log.info("Ok!")
        
        except:
            self.log.error(Log.formatError(sys.exc_info()))
            sys.exit()
    
    def clickToRenew(self):
        try:
            self.log.info("Removendo o registro padrão")
            
            xpath = '//div[@id="screener-criteria"]/div[2]/div/div/div/div/div[2]/ul/li/button'
            self.firefox.find_element_by_xpath(xpath).click()
            self.log.info("Ok!")
        except:
            self.log.error(Log.formatError(sys.exc_info()))
            sys.exit()

    def clickToSelectRegion(self): 
        self.log.info("Clicando para abrir as opções de região")
        
        xpath = '//div[@id="screener-criteria"]/div[2]/div/div/div/div/div[2]/ul/li'
        self.firefox.find_element_by_xpath(xpath).click()
        self.log.info("Ok!")
    
    def selectRegion(self, region):
        self.log.info("Selecionando a região " + region)
        try:
            self.firefox.find_element_by_xpath(".//*[contains(text(), '"+region+"')]").click()
        except NoSuchElementException as nsee: 
            self.log.info("A região " + region + " não existe.")          
            return False
        
        self.log.info("Ok!")
        return True        
    
    def clickToPerformQuery(self):
        try:
            if self.checkLoadPage():
                self.log.info("A página não foi capaz de carregar")            
                sys.exit()
            else:
                self.log.info("Realizando a consulta")
                '''Clicar para realizar a consulta'''
                xpath = '//div[@id="screener-criteria"]/div[2]/div/div[3]/button'

                self.log.info("Aguardando no máximo 20 segundos até o botão liberar")
                wait = WebDriverWait(self.firefox, 20)
                bt = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

                bt.click()

                self.log.info("Alguns segundos passados, trocando a página")
                window_after = self.firefox.window_handles[0]
                self.firefox.switch_to.window(window_after)

                self.log.info("Ok!")
        except:
            self.log.error(Log.formatError(sys.exc_info()))
            sys.exit()
    
    def iterateOverTable(self, xpath, dFinal):
        self.log.info("Aguardando no máximo 20 segundos até a tabela carregar")

        try:
            wait = WebDriverWait(self.firefox, 20)
            tabela = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

        except:
            self.log.error(Log.formatError(sys.exc_info()))
            return

        self.log.info("Tabela carregada, extraindo dados da tabela")

        rows = tabela.find_elements_by_tag_name('tbody')   
        
        try:
            for count,row in enumerate(rows):
                col = row.find_elements_by_tag_name("td")
                
                for count, item in enumerate(col):                
                    
                    mod = count%10
                    if mod == 0:
                        dFinal[col[count].text] = {"symbol":col[count].text, "name":col[count+1].text, "price":col[count+2].text}
            
        except StaleElementReferenceException as sere:
            self.log.info("A página não carregou corretamente.")
            return 
        
        except:
            self.log.error(Log.formatError(sys.exc_info()))
            return
    
    def extractDataTable(self):
        xpath = '//div[@id="scr-res-table"]/div/table'
        
        numberIterator = self.detectNumberIterations()
        if numberIterator == 0:
            return {}

        dFinal = {}
        for count, _ in enumerate(range(0, numberIterator)):
            if self.checkLoadPage():
                self.log.info("A página não foi capaz de carregar, tentando novamente")                            

            self.iterateOverTable(xpath, dFinal)
            
            if self.checkLoadPage():
                self.log.info("A página não foi capaz de carregar")            
                return self.dFinal

            else:
                try:
                    self.log.info("Página "+ str(count+1) + " recuperada.")
                    self.log.info("")
                    
                    try:
                        self.firefox.find_element_by_xpath(".//span[contains(text(), 'Next')]").click()

                    except NoSuchElementException as nsee:
                        '''Não tem o elemento Next, não tem paginação'''
                        self.log.info("Faltou o elemento Next, provavelmente não tem paginação.")
                        
                    self.log.info("Aguardando no máximo 25 segundos após clicar na paginação.")
                    time.sleep(5)
                    WebDriverWait(self.firefox, 20)

                except:
                    self.log.error(Log.formatError(sys.exc_info()))
                    return self.dFinal

            self.log.info("Alguns segundos passados, trocando a página")
    
        self.log.info("Ok!")

        return dFinal
    
    def checkLoadPage(self):
        '''Verifica se existem mensagens na paǵina indicando que houve falha no carregamento'''
        try:
            keywords = ["We’re sorry, we weren’t able to find any data.", "Unable to load Screener"]

            conditions = " or ".join(["contains(., '%s')" % keyword for keyword in keywords])
            expression = "//span[%s]" % conditions

            a = self.firefox.find_element_by_xpath(expression)   
            self.firefox.refresh()        
            return True

        except NoSuchElementException as nsee:           
            return False
        
        except:
            self.log.error(Log.formatError(sys.exc_info()))
    
    def detectNumberIterations(self):
        '''Verifica quantas páginas existem para parametriza o for'''
        try:
            self.log.info("Aguardando no máximo 10 segundos para os números carregarem")
            xpath = ".//span[contains(., '1-') and contains(., ' results')]"
            wait = WebDriverWait(self.firefox, 10)
            numbers = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            
            a = numbers.text
            pn = int(a.split(" ")[0].split("-")[1])
            tn = int(a.split(" ")[2])

            if pn == 0:
                return 0
            return math.ceil(tn/pn)

        except:
            self.log.error(Log.formatError(sys.exc_info()))
            sys.exit()