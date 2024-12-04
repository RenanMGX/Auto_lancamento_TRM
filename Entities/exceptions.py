class LoginRequired(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class ElementNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class CODIGONotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class AgenciaContaNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class BadRequest(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Desconectado(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class PageNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class AplicacaoResgateNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class FileMoviDiariaNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class FileLancamentoNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ColunaNotFoud(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        