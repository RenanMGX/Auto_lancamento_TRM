from getpass import getuser
import os
from View.view import Ui_Interface
from Entities.app_config import AppConfig
from Entities.tratar_dados import TratarDados
from typing import Literal

class File(AppConfig):
    @property
    def empty(self) -> bool:
        if self.Tela0_text.text() == "Vazio":
            return True
        else:
            if not os.path.exists(self.Tela0_text.text()):
                return True
        return False
    
    def __init__(self, view:Ui_Interface, file_tag:Literal['path_movi_diaria', 'path_lancamento']):
        super().__init__()
        self.view = view
        
        
        if file_tag == 'path_movi_diaria':
            self.Tela0_text = self.view.Tela0_text_moviDiaria
        elif file_tag == 'path_lancamento':
            self.Tela0_text = self.view.Tela0_text_lancamento
        
        file_path = self.load().get(file_tag)

        if file_path:
            
            try:
                if TratarDados.verificar_files(path=file_path, tipo=file_tag):
                    self.Tela0_text.setText(file_path)
                    self.file_path:str= file_path

            except Exception as err:
                self.remove(file_tag)
                self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}")
        else:
            self.file_path:str= "None"
        self.file_tag = file_tag
                
                
    def procurar_file(self):
        path = ""
        try:
            path = self.view.procurar_file()
            if path:
                if TratarDados.verificar_files(path=path, tipo=self.file_tag): #type: ignore
                    if self.file_tag == 'path_movi_diaria':
                        self.add(path_movi_diaria=path)
                    elif self.file_tag == 'path_lancamento':
                        self.add(path_lancamento=path)
                        
                    self.Tela0_text.setText(path)
                    self.file_path:str= path
                    #self.path_movi_diaria = path
                    return
        except Exception as err:
            #Logs().register(status='Report', description=str(err), exception=traceback.format_exc())
            self.view.alerta(title='Alerta', description=f"{type(err)}\n{str(err)}") 

if __name__ == "__main__":
    pass
