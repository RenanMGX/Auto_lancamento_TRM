from .navegador import Navegador, By, NoSuchElementException, P, WebElement, Keys, Select
import traceback
from . import exceptions
import re
import pandas as pd
from functools import wraps
from time import sleep
from datetime import datetime
from typing import Literal, List, Dict
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


class Bradesco:
    @property
    def Nav(self) -> Navegador:
        return self.__nav
        
    @staticmethod    
    def get_codigo(url:str) -> str:
        if (y:=re.search(r'(?<=CTRL=)[0-9]+', url)):
            return y.group()
        raise exceptions.CODIGONotFound(f"não foi possivel extrair o codigo do link '{url}'")
    
    @staticmethod
    def verificar_tela_branca(Nav:Navegador):
        try:
            Nav.find_element(By.XPATH, '/html/body[1]/div').click()
        except:
            pass
    
    
    def __init__(self, *, url:str="https://www.ne12.bradesconetempresa.b.br/ibpjlogin/login.jsf", nav_speak:bool=False, start_nav:bool=True) -> None:
        self.url:str = url
        self.nav_speak:bool = nav_speak
        
        if start_nav:
            self._start_nav()
            
        self.dados:Dict[str, list] = {
            'tipo': [],
            'agencia': [],
            'conta': [],
            'Dt. Aplicação': [],
            'Dt. Vencto': [],
            'Dt. Resgate': [],
            'Taxa (%)': [],
            'Vlr Princ': []
        }
        
        self.__current_codigo:str = ""
        

    def _start_nav(self):
        try:
            self.__nav
            self.__nav.close()
            del self.__nav
        except Exception:
            pass
        self.__nav:Navegador = Navegador(url=self.url, speak=self.nav_speak)
        
    def _exit(self):
        try:
            self.Nav.find_element(By.ID, 'botaoSair').click()
            print(P("Navegador encerrado!", color='cyan'))
            sleep(3)
        except AttributeError as err:
            pass
        try:
            self.Nav.close()
        except:
            pass
        try:
            del self.__nav
        except:
            pass
    

    def _get_empresas(self) -> dict:
        current_codigo = Bradesco.get_codigo(self.Nav.current_url)
        self.Nav.get(f"https://www.ne12.bradesconetempresa.b.br/ibpjtelainicial/acessarOutraEmpresa.jsf?CTRL={current_codigo}")
        Bradesco.verificar_tela_branca(self.Nav)
        
        tr_s =self.Nav.find_elements(By.TAG_NAME, 'tr')
        
        lista_empresas:dict = {}
        for tr in tr_s:
            try:
                lista_empresas[tr.text] = tr.find_element(By.TAG_NAME, 'input').get_attribute('value')
            except:
                pass
        
        return lista_empresas
    
    def _get_current_codigo(self):
        try:
            self.__current_codigo = Bradesco.get_codigo(self.Nav.current_url)
        except:
            pass
            #print(P("codigo da pagina atual não foi encontrado", color='red'))
    
    def _ir_pagina_central(self, codigo):
        self._get_current_codigo()
        self.Nav.get(f"https://www.ne12.bradesconetempresa.b.br/ibpjlogin/grupoeconomico.jsf?CTRL={self.__current_codigo}&codigoEmpresa={codigo}")
        Bradesco.verificar_tela_branca(self.Nav)
    
    def _ir_pagina_investimento(self):
        self._get_current_codigo()
        self.Nav.get(f"https://www.ne12.bradesconetempresa.b.br/ibpjextratoinvestimentos/entrada.jsf?CTRL={self.__current_codigo}&amp;car=ISE")
        Bradesco.verificar_tela_branca(self.Nav)
    
    def _select_mes(self, date:datetime=datetime.now()) -> bool:
        self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:tipoConsultaPorMes').click()
        
        tag_select_meses = self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:comboPeriodoMes')
        codigo_mes = [x.get_attribute('value') for x in tag_select_meses.find_elements(By.TAG_NAME, 'option') if date.strftime('%B').lower() in x.text.lower()][0]
        
        for _ in range(len(tag_select_meses.find_elements(By.TAG_NAME, 'option'))):
            if tag_select_meses.get_attribute('value') == codigo_mes:
                return True
            tag_select_meses.send_keys(Keys.DOWN)
        return False
    
    def _select_alteration(self, id, *, list_pular:List[str], orient:Literal['Down', 'Up'] = 'Down') -> bool:   
        try:
            tag = self.Nav.find_element(By.ID, id)

            codigo = tag.get_attribute('value')
            
            if orient == 'Down':
                key = Keys.DOWN
            elif orient == 'Up':
                key = Keys.UP
            
            tag.send_keys(key)
            
            for pular in list_pular:
                if Select(tag).first_selected_option.text == pular:
                    tag.send_keys(key)
            
            if tag.get_attribute('value') != codigo:
                return True
            return False
        except:
            return False
    
    def _coletar_dados(self) -> None:
        agencia, conta = re.split(r'[ ]+[|][ ]+', self.Nav.find_element(By.ID, 'formExtratoMovimentacao:_id328').text)
        
        self.Nav.find_element(By.XPATH, '//*[@id="formExtratoMovimentacao"]/div[1]/div[5]/div/table/tbody[8]/tr/td/span[2]').click()
        resgate_table = self.Nav.find_element(By.XPATH, '//*[@id="formExtratoMovimentacao"]/div[1]/div[5]/div/table/tbody[9]')
        for tr in resgate_table.find_elements(By.TAG_NAME, 'tr'):
            if (tr.text) and (not 'Total' in tr.text):
                text_temp:list = tr.text.split(' ')
                
                self.dados['tipo'].append('Resgate')
                
                self.dados['agencia'].append(agencia)
                self.dados['conta'].append(conta)
                
                self.dados['Dt. Aplicação'].append(text_temp[0])
                self.dados['Dt. Vencto'].append(text_temp[1])
                self.dados['Dt. Resgate'].append(text_temp[2])
                self.dados['Taxa (%)'].append(text_temp[3])
                self.dados['Vlr Princ'].append(text_temp[4])
        self.Nav.find_element(By.XPATH, '//*[@id="formExtratoMovimentacao"]/div[1]/div[5]/div/table/tbody[8]/tr/td/span[2]').click()

        self.Nav.find_element(By.XPATH, '//*[@id="formExtratoMovimentacao"]/div[1]/div[5]/div/table/tbody[5]/tr/td/span[2]').click()
        aplicacao_table = self.Nav.find_element(By.XPATH, '//*[@id="formExtratoMovimentacao"]/div[1]/div[5]/div/table/tbody[6]')
        for tr in aplicacao_table.find_elements(By.TAG_NAME, 'tr'):
            if (tr.text) and (not 'Total' in tr.text):
                text_temp:list = tr.text.split(' ')
                
                self.dados['tipo'].append('Aplicação')
                
                self.dados['agencia'].append(agencia)
                self.dados['conta'].append(conta)
                
                self.dados['Dt. Aplicação'].append(text_temp[0])
                self.dados['Dt. Vencto'].append(text_temp[1])
                self.dados['Dt. Resgate'].append(text_temp[2])
                self.dados['Taxa (%)'].append(text_temp[3])
                self.dados['Vlr Princ'].append(text_temp[4])
        
        self.Nav.find_element(By.XPATH, '//*[@id="formExtratoMovimentacao"]/div[1]/div[5]/div/table/tbody[5]/tr/td/span[2]').click()
        #return dados
        #import pdb; pdb.set_trace(header=P("_coletar_dados").pdb_header)

    def _get_ul_agenciaConta(self):
        for _ in range(60):
            try:
                ul_s:list = [x for x in self.Nav.find_elements(By.TAG_NAME, 'ul') if "Agência/conta:" in x.text]
                if not ul_s:
                    exceptions.AgenciaContaNotFound("o Campo 'Agência/conta:' não foi encontrado")
                ul:WebElement = ul_s[0]
                return ul
            except:
                sleep(1)
        raise Exception("não foi possivel adiquirir a UL da agencia e conta")
    
    def _select_agenciaConta(self, conta, *, timeout:int=5) -> bool:
        for _ in range(timeout):
            try:
                ul = self._get_ul_agenciaConta()
                
                _select = self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:_id73')
                if not _select.text:
                    _select.click()
                
                for li in ul.find_elements(By.TAG_NAME, 'li'):
                    if li.text == conta:
                        try:
                            li.click()
                            return True   
                        except:
                            ul.click()
                            print(traceback.format_exc())
                            return False
            except Exception as err:
                if _ >= (timeout - 1):
                    raise err
        return False
    
    def _get_agenciaConta(self, *, timeout:int=5) -> list:
        erro:Exception = Exception("Não conseguiu obter a agencia e conta")
        for _ in range(timeout):
            try:
                ul = self._get_ul_agenciaConta()
                self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:_id73').click()
                lista_de_contas = [x.text for x in ul.find_elements(By.TAG_NAME, 'li') if not "Agência/conta:" in x.text]
                ul.click()
                return lista_de_contas
            except Exception as err:
                erro = err
        raise erro
    
    def _get_tag_select_tipoInvestimento(self, *, control, count_lista_de_contas, tam_lista_de_contas, conta):
        try:
            tag_select_tipoInvestimento = Select(self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:comboTipoInvestimento'))
        except exceptions.ElementNotFound:
            print(P(f"Alerta {count_lista_de_contas}/{tam_lista_de_contas} - {conta} - Não existe Tipo de Investimento para essa conta ", color='magenta'))
            control["tipoInvestimento"] = []
            return False
                            
        if not control["tipoInvestimento"]:
            control["tipoInvestimento"] = [x.text for x in tag_select_tipoInvestimento.options if not x.text in ['Selecione']]
        control["tipoInvestimento"] = [x for x in control["tipoInvestimento"] if not x == '']
        
    def _iterar_contas(self, *, empresa:str, codigo:str):
        self._ir_pagina_central(codigo)
        
        self._ir_pagina_investimento()
        
        lista_de_contas = self._get_agenciaConta()

        tam_lista_de_contas = len(lista_de_contas)
        count_lista_de_contas = 1
        
        control:dict = {
            "tipoInvestimento" : [],
            "produto": []
        }
        
        for conta in lista_de_contas:
            control["tipoInvestimento"] = []
            control["produto"] = []
            for _ in range(5):
                try:
                    if self._select_agenciaConta(conta):
                        if self._select_mes(datetime.now()):
                            ###### Tipo de Documento
                            sleep(2)
                            while not self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:_id110').get_attribute('style') == 'display: none;':
                                sleep(1)
                            
                            if 'Para o período informado, nenhum extrato foi localizado.' in self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:divErro').text:
                                print(P(f"Alerta {count_lista_de_contas}/{tam_lista_de_contas} - {conta} - Não existe Tipo de Investimento para essa conta ", color='magenta'))
                                break
                            
                            #self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:_id110').get_attribute('style')
                            
                            for _ in range(5):
                                select_tipoInvestimento = self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:comboTipoInvestimento', timeout=30)
                                if not control["tipoInvestimento"]:
                                    select_tipoInvestimento.click()
                                    control["tipoInvestimento"] = [x.text for x in Select(select_tipoInvestimento).options if not x.text in ['Selecione']]
                                    select_tipoInvestimento.click()
                                control["tipoInvestimento"] = [x for x in control["tipoInvestimento"] if not x == '']
                                if control["tipoInvestimento"]:
                                    break
                                if _ >= 4:
                                    raise Exception("lista de tipoInvestimento vazia")
                            
                            for tipoInvestimento in control['tipoInvestimento']:
                                Select(self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:comboTipoInvestimento')).select_by_visible_text(tipoInvestimento)
                                ###############################
                                
                                ###################  Produtos            
                                if 'Para o período informado, nenhum extrato foi localizado.' in self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:divErro').text:
                                    print(P(f"Alerta {count_lista_de_contas}/{tam_lista_de_contas} - {conta} - Não existe produto para essa conta ", color='magenta'))
                                    #break
                                    import pdb; pdb.set_trace(header=P("parada sem encontrar o produto <---------------------------------- ").pdb_header)
                                    #raise Exception("")

                                for _ in range(5):
                                    select_produto = self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:comboProduto', timeout=30)
                                    if not control['produto']:
                                        select_produto.click()
                                        control["produto"] = [x.text for x in Select(select_produto).options if not x.text in ['Selecione', 'Todos os produtos']]
                                        select_produto.click()
                                    control["produto"] = [x for x in control["produto"] if not x == '']
                                    if control["produto"]:
                                        break
                                    if _ >= 4:
                                        raise Exception("lista de produtos vazia")
                                
                                for produto in control['produto']:
                                    Select(self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:comboProduto', timeout=30)).select_by_visible_text(produto)
                                ##########################
                            
                                    self.Nav.find_element(By.ID, 'formEntradaExtratoMovimentacao:_id130').click()
                                    self._coletar_dados()
                                    for _ in range(5):
                                        try:
                                            self.Nav.find_element(By.ID, 'formExtratoMovimentacao:_id642', timeout=1).click()
                                        except:
                                            pass
                                        
                                    control['produto'].remove(produto)
                                    
                                control['tipoInvestimento'].remove(tipoInvestimento)
                    print(P(f"Concuido {count_lista_de_contas}/{tam_lista_de_contas} - {conta}", color='green'))
                    break
                except Exception as err:
                    print(P(f"Error {count_lista_de_contas}/{tam_lista_de_contas} - {conta}", color='red'))
                    if "Message: stale element reference: stale element not found" in str(err):
                        print("WebElement não encontrado")
                    else:
                        print(err)
                        #traceback.format_exc()
                    
                    import pdb; pdb.set_trace(header=P(f"parada para o erro {count_lista_de_contas}/{tam_lista_de_contas} - {conta}  <---------------------------------- ").pdb_header)
                    self._ir_pagina_investimento()
                    
            
            count_lista_de_contas += 1

    def extract(self):
        while len(self.Nav.window_handles) > 1:
            self.Nav.switch_to.window(self.Nav.window_handles[-1])
            self.Nav.close()
            self.Nav.switch_to.window(self.Nav.window_handles[0])
        
        try:
            self.Nav.find_element(By.ID, 'botaoSair')
        except exceptions.ElementNotFound:
            raise exceptions.LoginRequired("É necessario efetuar o login primeiro!")
        
        Bradesco.verificar_tela_branca(self.Nav)
        self._get_current_codigo()
        
        self.__empresas:dict = self._get_empresas()
        tamanho__empresas = len(self.__empresas)
        contar__empresas = 1
        for empresa, codigo in self.__empresas.items():
            print(P(f"Iniciando {contar__empresas}/{tamanho__empresas} : {empresa=}", color='cyan'))
            self._iterar_contas(empresa=empresa, codigo=codigo)
            contar__empresas += 1
            
        
        
        import pdb; pdb.set_trace(header=P("Está Logado!").pdb_header)

        #self.Nav.find_element(By.ID, 'paginaCentral').get_attribute("src")
        
if __name__ == "__main__":
    pass
        