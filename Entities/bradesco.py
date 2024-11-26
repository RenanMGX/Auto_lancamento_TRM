from .navegador import Navegador, By, NoSuchElementException, P
from . import exceptions


class Bradesco:
    @property
    def Nav(self) -> Navegador:
        return self.__nav
    def __init__(self, *, url:str="https://www.ne12.bradesconetempresa.b.br/ibpjlogin/login.jsf", nav_speak:bool=False, start_nav:bool=True) -> None:
        self.url:str = url
        self.nav_speak:bool = nav_speak
        
        if start_nav:
            self.start_nav()
    
    def start_nav(self):
        try:
            self.__nav
            self.__nav.close()
            del self.__nav
        except Exception:
            pass
        
        self.__nav:Navegador = Navegador(url=self.url, speak=self.nav_speak)
        
    def exit(self):
        try:
            self.bt_sair.click()
            print(P("Navegador encerrado!", color='cyan'))
        except AttributeError as err:
            pass
            #print(P("não foi possivel clicar no botão sair", color='red'))
            #print(P(f"{type(err)}; {str(err)}", color='red'))
        
        try:
            self.Nav.close()
        except:
            pass
        
        try:
            del self.__nav
        except:
            pass
        
        
    def extract(self):
        try:
            self.bt_sair = self.Nav.find_element(By.ID, 'botaoSair')
        except exceptions.ElementNotFound:
            raise exceptions.LoginRequired("É necessario efetuar o login primeiro!")
        
        #print(P("está logado!", color='green'))
        self.Nav.find_element(By.ID, '_id74_8:_id76').click()
        
        import pdb; pdb.set_trace(header=P("Está Logado!").pdb_header)

        
        
if __name__ == "__main__":
    pass
        