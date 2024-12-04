import os
import pandas as pd
import exceptions

class TratarDados:
    @staticmethod
    def verificar_movi_diaria(path:str) -> bool:
        if not os.path.exists(path):
            raise exceptions.FileMoviDiariaNotFound(f"Arquivo '{path}' não foi encontrado")
        
        if (path.endswith('.xlsx')) or (path.endswith('.xlsm')) or (path.endswith('.xls')):
            df = pd.read_excel(path, sheet_name="Saldo do Dia", skiprows=6)
            
            colunas = ["Empresa", "Divisão", " Agência", "Conta"]
            for coluna in colunas:
                if not coluna in df.keys():
                    raise exceptions.ColunaNotFoud(f"A coluna '{coluna}' não foi encontrada no arquivo\n '{path}'")
            
            #import pdb;pdb.set_trace()
            return True
        return False
    
    @staticmethod
    def verificar_lancamento(path:str) -> bool:
        if not os.path.exists(path):
            raise exceptions.FileLancamentoNotFound(f"Arquivo '{path}' não foi encontrado")
        
        if (path.endswith('.xlsx')) or (path.endswith('.xlsm')) or (path.endswith('.xls')):
            df = pd.read_excel(path, sheet_name="Extrato")
            
            colunas = ["Parceiro", "Empresa", "Divisão", "Banco", "Aplicação", "Dt. Vencto", "Dt. Resgate . Carência", "Taxa (%)", "Vlr Princ. (R$)", "Dt. Aplicação", "Dt. Resgate", "Vlr Princ", "Chave", "Lançamento", "Montante"]
            for coluna in colunas:
                if not coluna in df.keys():
                    raise exceptions.ColunaNotFoud(f"A coluna '{coluna}' não foi encontrada no arquivo\n '{path}'")
            
            #import pdb;pdb.set_trace()
            return True
        return False
    
    @staticmethod
    def criar(*,
        path_movi_diaria:str,
        path_lancamento:str
    ):
        pass
    
if __name__ == "__main__":
    TratarDados.verificar_lancamento(r'R:/informe de rendimento trm - Amanda/#material/Lançamentos - TRM Amanda Novo.. - .xlsm')
