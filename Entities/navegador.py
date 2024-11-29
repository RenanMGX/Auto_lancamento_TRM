from typing import List
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from getpass import getuser
from time import sleep
from functools import wraps
from Entities.dependencies.functions import P
import os
from . import exceptions
import sys

from selenium.webdriver.remote.webelement import WebElement

class Navegador(Chrome):    
    @property
    def path_download(self) -> str:
        return os.path.join(os.getcwd(), "Download_Arquivos")
    
    @staticmethod
    def check_badRequest(_super, *, value) -> WebElement:
        if isinstance(_super, type):
            _super = _super()
        nav:Chrome = _super #type: ignore
        
        element: WebElement = nav.find_element(By.TAG_NAME, 'html')
        if "Bad Request\nYour browser sent a request that this server could not understand.\nSize of a request header field exceeds server limit.".lower() in element.text.lower():
            print(f"Bad Request no {value=}")
            raise exceptions.BadRequest("Site não carregou corretamente")

        return element
    
        
    def __init__(self, *, url:str="", speak:bool=False): 
        self.speak:bool = speak 
        
        if not os.path.exists(self.path_download): 
            os.makedirs(self.path_download)
        prefs:dict = {"download.default_directory": self.path_download}
        chrome_options: Options = Options()
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument(f"--user-data-dir=C:\\Users\\{getuser()}\\AppData\\Local\\Google\\Chrome")
        
        super().__init__(options=chrome_options)
        if url:
            self.get(url)

    
    def find_element(
        self, 
        by=By.ID, 
        value: str | None = None, 
        *, 
        timeout:int=10, 
        force:bool=False, 
        wait_before:int|float=0, 
        wait_after:int|float=0
    ) -> WebElement:
        
        #element:WebElement = Navegador.check_badRequest(super(), value=value)
        
        if wait_before > 0:
            sleep(wait_before)
        for _ in range(timeout*4):
            try:
                result = super().find_element(by, value)
                print(P(f"({by=}, {value=}): Encontrado com!", color='green')) if self.speak else None
                if wait_after > 0:
                    sleep(wait_after)
                return result
            except NoSuchElementException:
                pass                

            sleep(.25)
        
        if force:
            print(P(f"({by=}, {value=}): não encontrado, então foi forçado!", color='yellow')) if self.speak else None
            return super().find_element(By.TAG_NAME, 'html')
        
        print(P(f"({by=}, {value=}): não encontrado! -> erro será executado", color='red')) if self.speak else None
        raise exceptions.ElementNotFound(f"({by=}, {value=}): não encontrado!")

    def find_elements(
        self, 
        by=By.ID, 
        value: str | None = None, 
        *, 
        timeout:int=10, 
        force:bool=False,
        wait_before:int|float=0, 
        wait_after:int|float=0
    ) -> List[WebElement]:
        
        
        if wait_before > 0:
            sleep(wait_before)
        for _ in range(timeout*4):
            try:
                result = super().find_elements(by, value)
                print(P(f"({by=}, {value=}): Encontrado com Sucesso!", color='green')) if self.speak else None
                if wait_after > 0:
                    sleep(wait_after)
                return result
            except NoSuchElementException:
                pass                

            sleep(.25)
        
        if force:
            print(P(f"({by=}, {value=}): não encontrado, então foi forçado!", color='yellow')) if self.speak else None
            return []
        
        print(P(f"({by=}, {value=}): não encontrado! -> erro será executado", color='red')) if self.speak else None
        raise exceptions.ElementNotFound(f"({by=}, {value=}): não encontrado!")

if __name__ == "__main__":
    pass
