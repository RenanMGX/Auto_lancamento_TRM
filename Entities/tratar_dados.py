import os
import pandas as pd
import exceptions
from dependencies.functions import P, Functions
from typing import Literal
import xlwings as xw
from xlwings.main import Book, Sheet
import shutil
from tkinter import filedialog
from datetime import datetime
from PyQt5 import QtWidgets

def remover_zero_esquerda(value:str):
    while value[0] == "0":
        value = value[1:]
    return value

def get_empresa_conta(row:pd.Series, df_movi_diaria:pd.DataFrame, _type:Literal['Empresa', 'Divisão']):
    empresa = df_movi_diaria[
        (df_movi_diaria[' Agência'] == row['agencia']) &
        (df_movi_diaria['Conta'] == remover_zero_esquerda(row['conta']))
    ][_type]
    
    return empresa.iloc[0] if not empresa.empty else ""

class TratarDados:
    @staticmethod
    def _verificar_movi_diaria(path:str) -> bool:
        if not os.path.exists(path):
            raise exceptions.FileMoviDiariaNotFound(f"Arquivo '{path}' não foi encontrado")
        
        if (path.endswith('.xlsx')) or (path.endswith('.xlsm')) or (path.endswith('.xls')):
            df = pd.read_excel(path, sheet_name="Saldo do Dia", skiprows=6)
            
            colunas = ["Empresa", "Divisão", " Agência", "Conta"]
            for coluna in colunas:
                if not coluna in df.keys():
                    raise exceptions.ColunaNotFoud(f"A coluna '{coluna}' não foi encontrada no arquivo\n '{path}'")
            
            del df
            #import pdb;pdb.set_trace()
            return True
        return False
    
    @staticmethod
    def _verificar_lancamento(path:str) -> bool:
        if not os.path.exists(path):
            raise exceptions.FileLancamentoNotFound(f"Arquivo '{path}' não foi encontrado")
        
        if (path.endswith('.xlsx')) or (path.endswith('.xlsm')) or (path.endswith('.xls')):
            df = pd.read_excel(path, sheet_name="Extrato")
            
            colunas = ["Parceiro", "Empresa", "Divisão", "Banco", "Aplicação", "Dt. Vencto", "Dt. Resgate . Carência", "Taxa (%)", "Vlr Princ. (R$)", "Dt. Aplicação", "Dt. Resgate", "Vlr Princ", "Chave", "Lançamento", "Montante"]
            for coluna in colunas:
                if not coluna in df.keys():
                    raise exceptions.ColunaNotFoud(f"A coluna '{coluna}' não foi encontrada no arquivo\n '{path}'")
            
            del df
            #import pdb;pdb.set_trace()
            return True
        return False
    
    @staticmethod
    def verificar_files(*, path:str, tipo: Literal['path_movi_diaria', 'path_lancamento']) -> bool:
        if tipo == 'path_lancamento':
            return TratarDados._verificar_lancamento(path)
        elif tipo == 'path_movi_diaria':
            return TratarDados._verificar_movi_diaria(path)
        raise Exception("verificar_files() não identificado")
    
    @staticmethod
    def transformar(*,
        path_movi_diaria:str,
        path_lancamento:str,
        path_baseInvestimentos:str,
        start_date:datetime,
        end_date:datetime|None
    ):
        data_para_nome = lambda: datetime.now().strftime("%Y%m%d%H%M%S_")
        
        df_investimentos = pd.read_excel(path_baseInvestimentos)
        df_investimentos['Empresa'] = ""
        df_investimentos['Divisão'] = ""
        
        df_movi_diaria = pd.read_excel(path_movi_diaria, sheet_name="Saldo do Dia", skiprows=6)
        
        df_investimentos['Empresa'] = df_investimentos.apply(lambda row: get_empresa_conta(row, df_movi_diaria, 'Empresa'), axis=1)
        df_investimentos['Divisão'] = df_investimentos.apply(lambda row: get_empresa_conta(row, df_movi_diaria, 'Divisão'), axis=1)
        df_investimentos['Taxa (%)'] = df_investimentos['Taxa (%)'].str.replace(".", "").str.replace(",", ".").astype(float)
        df_investimentos['Vlr Princ'] = df_investimentos['Vlr Princ'].str.replace(".", "").str.replace(",", ".").astype(float)
        df_investimentos['Dt. Aplicação'] = pd.to_datetime(df_investimentos['Dt. Aplicação'], format="%d/%m/%Y", errors='coerce')
        df_investimentos['Dt. Vencto'] = pd.to_datetime(df_investimentos['Dt. Vencto'], format="%d/%m/%Y", errors='coerce')
        df_investimentos['Dt. Resgate'] = pd.to_datetime(df_investimentos['Dt. Resgate'], format="%d/%m/%Y", errors='coerce')
        
        #if end_date:
            
        
        resgate = df_investimentos[df_investimentos['tipo'] == 'Resgate']
        resgate = resgate[['Empresa', 'Divisão', 'Dt. Aplicação', 'Dt. Vencto', 'Dt. Resgate', 'Taxa (%)', 'Vlr Princ']]
        
        aplicacao = df_investimentos[df_investimentos['tipo'] == 'Aplicação']
        aplicacao['Parceiro'] = 600013
        aplicacao = aplicacao[['Parceiro', 'Empresa', 'Divisão', 'Dt. Aplicação', 'Dt. Vencto', 'Dt. Resgate', 'Taxa (%)', 'Vlr Princ']]
        
        if end_date:
            resgate = resgate[
                (resgate['Dt. Resgate'] >= start_date) &
                (resgate['Dt. Resgate'] <= end_date) 
            ]
            aplicacao = aplicacao[
                (aplicacao['Dt. Aplicação'] >= start_date) &
                (aplicacao['Dt. Aplicação'] <= end_date) 
            ]
        else:
            aplicacao = aplicacao[aplicacao['Dt. Aplicação'] == start_date]
            resgate = resgate[resgate['Dt. Resgate'] == start_date]
        
        path_lancamento_temp = os.path.join(os.getcwd(), f"{data_para_nome()}temporario_{os.path.basename(path_lancamento)}")
        
        
        #import pdb;pdb.set_trace(header=P("transformar()").pdb_header)
        
        shutil.copy(path_lancamento, path_lancamento_temp)
        
        
        app = xw.App(visible=False)
        with app.books.open(path_lancamento_temp)as wb:
            ws:Sheet = wb.sheets['Extrato']
            ws.activate()
            
            ws.range('B2:D' + str(ws.cells.last_cell.row)).clear_contents()
            ws.range('D2:D' + str(ws.cells.last_cell.row)).number_format = "@"
            ws.range("B2").value = aplicacao[['Parceiro', 'Empresa', 'Divisão']].values
            
            ws.range('G2:K' + str(ws.cells.last_cell.row)).clear_contents()
            ws.range("G2").value = aplicacao[['Dt. Aplicação', 'Dt. Vencto', 'Dt. Resgate', 'Taxa (%)', 'Vlr Princ']].values
            
            ws.range('V2:AB' + str(ws.cells.last_cell.row)).clear_contents()
            ws.range('W2:W' + str(ws.cells.last_cell.row)).number_format = "@"
            ws.range("V2").value = resgate.values
            
            #import pdb;pdb.set_trace(header=P("xlwings").pdb_header)
            try:
                options = QtWidgets.QFileDialog.Options()
                path, _ = QtWidgets.QFileDialog.getSaveFileName(
                    None,
                    "Salvar Arquivo",
                    "Lançamentos - TRM.xlsm",  # Nome de arquivo padrão
                    "Excel Files (*.xlsm);;All Files (*)",  # Tipos de arquivos
                    options=options
                )
            except:
                path = filedialog.asksaveasfilename(initialfile="Lançamentos - TRM.xlsm",defaultextension=".xlsm", filetypes=[("Excel", ".xlsm")])
            if not path:
                path = os.path.join(os.getcwd(), f"{data_para_nome()}Lançamentos - TRM.xlsm")
                
            wb.save(path)
            
        
        Functions.fechar_excel(path_lancamento_temp)
        Functions.fechar_excel("Pasta1")
        try:
            app.kill()
        except:
            pass
        try:
            os.unlink(path_lancamento_temp)
        except:
            pass
        #import pdb;pdb.set_trace(header=P("transformar()").pdb_header)
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TratarDados.transformar(
        path_movi_diaria=r'R:/informe de rendimento trm - Amanda/#material/Movimentação diária.xlsm',
        path_lancamento=r'R:/informe de rendimento trm - Amanda/#material/Lançamentos - TRM Amanda Novo.. - .xlsm',
        path_baseInvestimentos=r'R:\informe de rendimento trm - Amanda\Arquivos-Bot\dados_extraidos-05122024175002-.xlsx',
        start_date=datetime(2024,12,1),
        end_date=datetime.now()
    )
