from typing import Dict
from getpass import getuser

default:Dict[str, Dict[str,object]] = {
    'credential': {
        'crd': 'SAP_PRD',
        'email': 'Microsoft-RPA'
    },
    'path': {
        'plano_contas': f'C:\\Users\\{getuser()}\\PATRIMAR ENGENHARIA S A\\RPA - Documentos\\RPA - Dados\\Contas Contabeis\\Plano de Contas.XLSX'
    },
    'log': {
        'hostname': 'Patrimar-RPA',
        'port': '80',
        'token': ''
    },
    'email': {
        'destino': 'EMAIL DO DESTINO'
    }
}