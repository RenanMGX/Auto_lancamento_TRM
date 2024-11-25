from Entities.bradesco import Bradesco, By
from View.view import Ui_Interface, QtWidgets
from Entities.app_config import AppConfig
import sys
import os
from Entities.dependencies.logs import Logs, traceback


class Controller:
    def __init__(self) -> None:
        self.bradesco = Bradesco(url="https://www.ne12.bradesconetempresa.b.br/ibpjlogin/login.jsf", nav_speak=True, start_nav=False)
        self.app_config = AppConfig()
        self.view = Ui_Interface()
        
        self.initial_config()
        
    def initial_config(self):
        if (path_movi_diaria:=self.app_config.load().get('path_movi_diaria')):
            if os.path.exists(path_movi_diaria):
                self.view.Tela0_text_moviDiaria.setText(path_movi_diaria)
        
        self.view.Tela0_bt_moviDiaria.clicked.connect(self.procurar_file_moviDiaria)
        self.view.Tela0_bt_iniciarNavegador.clicked.connect(self.iniciar_navegador)
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
    
    def iniciar_navegador(self) -> None:
        try:
            try:
                self.bradesco.Nav
                self.bradesco.Nav.find_element(By.TAG_NAME, 'html')
                self.view.alerta(title='Alerta', description="Navegador já esta aberto")
            except:
                self.bradesco.start_nav()
                self.view.Tela0_bt_iniciarExtract.setVisible(True)
                return
        except:
            self.bradesco.exit()
        self.view.Tela0_bt_iniciarExtract.setVisible(False)
    
     
    def iniciar_extrac(self):
        self.bradesco.extract()
        
        
if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        controle = Controller()
        controle.view.show()
        sys.exit(app.exec_())
    except Exception as err:
        print(err)
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())