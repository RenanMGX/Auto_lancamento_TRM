from Entities.bradesco import Bradesco, By, P
from Entities.tratar_dados import TratarDados
from View.view import Ui_Interface, QtWidgets
import sys
import os
from Entities.dependencies.logs import Logs, traceback
from functools import wraps
from datetime import datetime
import pandas as pd
import locale
from files_validate import File
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
        self.bradesco = Bradesco(url="https://www.ne12.bradesconetempresa.b.br/ibpjlogin/login.jsf", nav_speak=False, start_nav=False)
        self.view = Ui_Interface(nav=self.bradesco)
        
        self.initial_config()
        
        self.__importantFilesPath:str = os.path.join(os.getcwd(), "Arquivos-Bot")
        if not os.path.exists(self.__importantFilesPath):
            os.makedirs(self.__importantFilesPath)

    def __navOpen(self) -> bool:
        try:
            self.bradesco.Nav
            self.bradesco.Nav.find_element(By.TAG_NAME, 'html')
            return True
        except:
            return False

    def verificar_arquivos(self):
        liberado = True
        if self.movi_diaria.empty:
            liberado = False
            
        if self.lancamento.empty:
            liberado = False
         
        if liberado:
            #self.view.Tela0_bt_iniciarNavegador.setVisible(True)
            if self.__navOpen():
                self.view.Tela0_bt_iniciarExtract.setVisible(True)
        else:
            #self.view.Tela0_bt_iniciarNavegador.setVisible(False)
            self.view.Tela0_bt_iniciarExtract.setVisible(False)
        
        return liberado
     
        
    def initial_config(self):
        self.movi_diaria = File(view=self.view, file_tag='path_movi_diaria')
        
        self.lancamento = File(view=self.view, file_tag='path_lancamento')
                        
        self.verificar_arquivos()   
        
        self.view.Tela0_bt_moviDiaria.clicked.connect(self.procurar_file_moviDiaria)
        self.view.Tela0_bt_lancamento.clicked.connect(self.procurar_file_lancamento)
        self.view.Tela0_bt_iniciarNavegador.clicked.connect(self.pre_iniciar_navegador)
        self.view.Tela0_bt_iniciarExtract.clicked.connect(self.iniciar_extrac)
        
        self.view.Tela0_bt_teste.clicked.connect(self.test) #<<<<<<<<< Teste
    
    #@hide_show            
    def procurar_file_moviDiaria(self, *args, **kwargs) -> None:
        self.movi_diaria.procurar_file()
        self.verificar_arquivos()  
    
    #@hide_show    
    def procurar_file_lancamento(self, *args, **kwargs) -> None:
        self.lancamento.procurar_file()
        self.verificar_arquivos()  
    
    @hide_show
    def pre_iniciar_navegador(self, *args, **kwargs):
        self.iniciar_navegador()
        
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
        if self.verificar_arquivos():
            try:
                agora = datetime.now()
                self.iniciar_navegador(alert=False)
                self.bradesco.extract(date=self.view.date)
                self.bradesco._exit()
                
                tempo_extracao = datetime.now() - agora
                
                file_path = os.path.join(self.__importantFilesPath, datetime.now().strftime('dados_extraidos-%d%m%Y%H%M%S-.xlsx'))
                pd.DataFrame(self.bradesco.dados).to_excel(file_path, index=False)
                
                self.transformarDados(file_path)   
                
                self.view.Tela0_bt_iniciarExtract.setVisible(False)
                
                self.view.alerta(title='Concluido', description=f"Extração de dados Concluida em  \n  {tempo_extracao}    ")
                
                return
                
            except Exception as err:
                print(P("Alerta de Erro", color='magenta'))
                print(traceback.format_exc())
                self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}")
            return
        else:
            self.view.alerta(title='Alerta', description="Revise os arquivos informados")
    
    def transformarDados(self, path_baseInvestimentos:str):
        TratarDados.transformar(
            path_movi_diaria=self.movi_diaria.file_path,
            path_lancamento=self.lancamento.file_path,
            path_baseInvestimentos=path_baseInvestimentos
        )
        
    def test(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Salvar Arquivo",
            "Lançamentos - TRM.xlsm",  # Nome de arquivo padrão
            "Excel Files (*.xlsm);;All Files (*)",  # Tipos de arquivos
            options=options
        )
        print(file_path, "\n",_)
        
if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        controle = Controller()
        controle.view.show()
        sys.exit(app.exec_())
    except Exception as err:
        print(P("Alerta de Erro", color='magenta'))
        print(traceback.format_exc())        
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
        input("Erro ")
        