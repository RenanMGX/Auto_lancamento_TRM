import os
import json
from getpass import getuser

class AppConfig:
    @property
    def path(self) -> str:
        return self.__path
    
    def __init__(self, path:str=f"C:\\Users\\{getuser()}", folder:str=".informe_rendimento_trm", file:str="config.json"):
        if not file.endswith(".json"):
            file += ".json"
        if os.path.exists(path):
            path = os.path.join(path, folder)
            
            if not os.path.exists(path):
                os.makedirs(path)
            
            path = os.path.join(path, file)
            if not os.path.exists(path):
                self.__save({})
                    
            self.__path = path
            
        else:
            raise Exception(f"caminho '{path}' não encontrado!")
        
    def __save(self, value: dict) -> None:
        with open(self.path, 'w', encoding='utf-8')as _file:
            json.dump(value, _file)
    
    def load(self) -> dict:
        try:
            with open(self.path, 'r', encoding='utf-8')as _file:
                return json.load(_file)
        except:
            self.__save({})
            with open(self.path, 'r', encoding='utf-8')as _file:
                return json.load(_file)
        
    def add(self, **kwargs) -> None:
        values:dict = self.load()
        for key, value in kwargs.items():
            values[key] = value
        self.__save(values)
        
    def remove(self, delete_arg) -> None:
        values:dict = self.load()
        try:
            del values[delete_arg]
        except:
            print("erro ao apagar")
        self.__save(values)
        
    def alter(self, **kwargs) -> None:
        for key, value in kwargs.items():
            self.remove(key)
            
        self.add(**kwargs)
        
    def _reset(self) -> None:
        self.__save({})
    
        
if __name__ == "__main__":
    bot = AppConfig()
    print(bot.load())
    bot.remove("path_movi_diaria")
    