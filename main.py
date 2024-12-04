from Entities.bradesco import Bradesco, By, P
from Entities.tratar_dados import TratarDados
from View.view import Ui_Interface, QtWidgets
from Entities.app_config import AppConfig
import sys
import os
from Entities.dependencies.logs import Logs, traceback
from functools import wraps
from datetime import datetime
import pandas as pd
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class Controller:
    @staticmethod   
    def hide_show(func):
        def wrap(*args, **kwargs):
            self:Controller = args[0]
            self.view.hide()
            try:
                result = func(*args, **kwargs)
            finally:
                self.view.show()
            return result
        return wrap


    def __init__(self) -> None:
        self.bradesco = Bradesco(url="https://www.ne12.bradesconetempresa.b.br/ibpjlogin/login.jsf", nav_speak=True, start_nav=False)
        self.app_config = AppConfig()
        self.view = Ui_Interface(nav=self.bradesco)
        
        self.initial_config()
        
        self.__importantFilesPath:str = os.path.join(os.getcwd(), "Arquivos-Bot")
        if not os.path.exists(self.__importantFilesPath):
            os.makedirs(self.__importantFilesPath)
        
    def initial_config(self):
        if (path_movi_diaria:=self.app_config.load().get('path_movi_diaria')):
            try:
                if TratarDados.verificar_movi_diaria(path_movi_diaria):
                    self.view.Tela0_text_moviDiaria.setText(path_movi_diaria)
                    self.path_movi_diaria = path_movi_diaria
            except Exception as err:
                self.app_config.remove("path_movi_diaria")
                self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}") 
                
        if (path_lancamento:=self.app_config.load().get('path_lancamento')):
            try:
                if TratarDados.verificar_lancamento(path_lancamento):
                    self.view.Tela0_text_lancamento.setText(path_lancamento)
                    self.path_lancamento = path_lancamento
            except Exception as err:
                self.app_config.remove("path_lancamento")
                self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}") 
                
        
        self.view.Tela0_bt_moviDiaria.clicked.connect(self.procurar_file_moviDiaria)
        self.view.Tela0_bt_lancamento.clicked.connect(self.procurar_file_lancamento)
        self.view.Tela0_bt_iniciarNavegador.clicked.connect(self.pre_iniciar_navegador)
        self.view.Tela0_bt_iniciarExtract.clicked.connect(self.iniciar_extrac)
        
        self.view.Tela0_bt_teste.clicked.connect(self.transformarDados) #<<<<<<<<< Teste
    
    @hide_show            
    def procurar_file_moviDiaria(self, *args, **kwargs) -> None:
        path = ""
        try:
            path = self.view.procurar_file()
            if path:
                if TratarDados.verificar_movi_diaria(path):
                    self.app_config.add(path_movi_diaria=path)
                    self.view.Tela0_text_moviDiaria.setText(path)
                    self.path_movi_diaria = path
                    return
        except Exception as err:
            #Logs().register(status='Report', description=str(err), exception=traceback.format_exc())
            self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}") 
    
    @hide_show    
    def procurar_file_lancamento(self, *args, **kwargs) -> None:
        path = ""
        try:
            path = self.view.procurar_file()
            if path:
                if TratarDados.verificar_lancamento(path):
                    self.app_config.add(path_lancamento=path)
                    self.view.Tela0_text_lancamento.setText(path)
                    self.path_lancamento = path
                    return
                else:
                    self.view.alerta(title='Alerta', description=f"selecione apenas arquivos Excel!")
                    return
        except Exception as err:
            #Logs().register(status='Report', description=str(err), exception=traceback.format_exc())
            self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}")  
    
    def pre_iniciar_navegador(self):
        self.iniciar_navegador()
        
    @hide_show
    def iniciar_navegador(self, alert:bool=True) -> None:
        if self.__navOpen():
            if alert:
                self.view.alerta(title='Alerta', description="Navegador já esta aberto")
            self.view.Tela0_bt_iniciarExtract.setVisible(True)
            return
        
        try:
            self.bradesco._start_nav()
            self.view.Tela0_bt_iniciarExtract.setVisible(True)
        except:
            print(traceback.format_exc())
            self.bradesco._exit()
            self.view.Tela0_bt_iniciarExtract.setVisible(False)
    
    @hide_show 
    def iniciar_extrac(self, *args, **kwargs):
        try:
            self.iniciar_navegador(alert=False)
            self.bradesco.extract(date=datetime.now())
            
            file_path = os.path.join(self.__importantFilesPath, datetime.now().strftime('dados_extraidos-%d%m%Y%H%M%S-.xlsx'))
            pd.DataFrame(self.bradesco.dados).to_excel(file_path, index=False)
                   
            #self.baseDataPath:str = file_path
            
            return
            
        except Exception as err:
            self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}")
        return
            
            
    def __navOpen(self) -> bool:
        try:
            self.bradesco.Nav
            self.bradesco.Nav.find_element(By.TAG_NAME, 'html')
            return True
        except:
            return False
    
    
    def transformarDados(self):
        lancamento_file = self.view.procurar_file()
        if not lancamento_file:
            lancamento_file = os.path.join(os.getcwd(), datetime.now().strftime("Lançamentos - TRM - %d%m%Y%H%M%S .xlsm"))
        
        print(lancamento_file)
        TratarDados.criar(
            path_movi_diaria=self.path_movi_diaria,
            path_lancamento=lancamento_file
        )
        
        
if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        controle = Controller()
        controle.view.show()
        sys.exit(app.exec_())
    except Exception as err:
        print(err)
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
        