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