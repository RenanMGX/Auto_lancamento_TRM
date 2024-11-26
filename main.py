from Entities.bradesco import Bradesco, By, P
from View.view import Ui_Interface, QtWidgets
from Entities.app_config import AppConfig
import sys
import os
from Entities.dependencies.logs import Logs, traceback
from functools import wraps



class Controller:
    def __init__(self) -> None:
        self.bradesco = Bradesco(url="https://www.ne12.bradesconetempresa.b.br/ibpjlogin/login.jsf", nav_speak=True, start_nav=False)
        self.app_config = AppConfig()
        self.view = Ui_Interface(nav=self.bradesco)
        
        self.initial_config()
    
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
    
        
    def initial_config(self):
        if (path_movi_diaria:=self.app_config.load().get('path_movi_diaria')):
            if os.path.exists(path_movi_diaria):
                self.view.Tela0_text_moviDiaria.setText(path_movi_diaria)
        
        self.view.Tela0_bt_moviDiaria.clicked.connect(self.procurar_file_moviDiaria)
        self.view.Tela0_bt_iniciarNavegador.clicked.connect(self.pre_iniciar_navegador)
        self.view.Tela0_bt_iniciarExtract.clicked.connect(self.iniciar_extrac)
                
    def procurar_file_moviDiaria(self) -> None:
        path = ""
        try:
            path = self.view.procurar_file()
            if os.path.exists(path):
                if (path.endswith('.xlsx')) or (path.endswith('.xlsm')) or (path.endswith('.xls')):
                    self.app_config.add(path_movi_diaria=path)
                    self.view.Tela0_text_moviDiaria.setText(path)
                    return
                else:
                    self.view.alerta(title='Alerta', description=f"selecione apenas arquivos Excel!")
                    return
        except Exception as err:
            Logs().register(status='Report', description=str(err), exception=traceback.format_exc())
        self.view.alerta(title='Alerta', description=f"o caminho {path=} não foi encontrado!")  
    
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
            self.bradesco.start_nav()
            self.view.Tela0_bt_iniciarExtract.setVisible(True)
        except:
            print(traceback.format_exc())
            self.bradesco.exit()
            self.view.Tela0_bt_iniciarExtract.setVisible(False)
    
    @hide_show 
    def iniciar_extrac(self, *args, **kwargs):
        try:
            self.iniciar_navegador(alert=False)
            self.bradesco.extract()
        except Exception as err:
            self.view.alerta(title='Alerta', description=str(err))
        return
            
            
    def __navOpen(self) -> bool:
        try:
            self.bradesco.Nav
            self.bradesco.Nav.find_element(By.TAG_NAME, 'html')
            return True
        except:
            return False
        
        
if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        controle = Controller()
        controle.view.show()
        sys.exit(app.exec_())
    except Exception as err:
        print(err)
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
        