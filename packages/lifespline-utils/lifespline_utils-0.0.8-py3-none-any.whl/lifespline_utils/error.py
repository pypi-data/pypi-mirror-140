"""_summary_."""

class LSUError(Exception):
    pass

class LSUInvalidArgumentsError(LSUError):
    """_summary_

    Args:
        LSUError (_type_): _description_
    """
    message: str

    def __init__(self, message):
        super().__init__(message)

class LSUInvalidSectionError(LSUError):
    """_summary_

    Args:
        LSUError (_type_): _description_
    """
    message: str

    def __init__(self, message):
        super().__init__(message)

class LSUInvalidSectionKeyError(LSUError):
    """_summary_

    Args:
        LSUError (_type_): _description_
    """
    message: str

    def __init__(self, message):
        super().__init__(message)


class LSUDuplicateConfigSectionsError(LSUError):
    """_summary_

    Args:
        LSUError (_type_): _description_
    """
    message: str

    def __init__(self, message):
        super().__init__(message)


class LSUNoSuchPathError(LSUError):
    """_summary_

    Args:
        LSUError (_type_): _description_
    """
    message: str

    def __init__(self, message):
        super().__init__(message)

class LSUNoSuchConfigFileError(LSUError):
    """No such configuration file

    Args:
        LSUError (_type_): _description_
    """
    message: str

    def __init__(self, message):
        super().__init__(message)

class LSUInvalidConfigFileFormatError(LSUError):
    """Invalid configuration file format

    Args:
        LSUError (_type_): _description_
    """    
    message: str

    def __init__(self, message):
        super().__init__(message)

class LSUPythonVirtualEnvironmentNotFoundError(LSUError):
    """The python virtual environment `.env` was not found.

    Args:
        LSUError (_type_): _description_
    """    
    message: str

    def __init__(self, message):
        super().__init__(message)
