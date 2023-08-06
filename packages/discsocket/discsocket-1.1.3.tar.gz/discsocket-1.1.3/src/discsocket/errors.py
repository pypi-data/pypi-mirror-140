class BaseException(Exception):
    def __init__(self, message):
        super().__init__(message)


class CommandNotFound(BaseException):
    def __init__(self, message):
        super().__init__(message)

class ComponentNotFound(BaseException):
    def __init__(self, message):
        super().__init__(message)