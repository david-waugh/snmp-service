from snmpservice.utils.logger import logger
from pydantic import BaseModel
from functools import wraps
from inspect import isclass

def exception_handler(raises=None):
    """
    Decorator to handle exceptions in wrapped functions.

    Keyword arguments:
    raises : Exception-like class : Class to raise if error encountered.
                                    Default=None, meaning to return None.

    Raises:
    Exception of class passed in "raises" kwarg. Default=None (raises nothing).
    If class passed in "raises" kwarg is not subclass of BaseException, raises Exception.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if isclass(raises):
                    if issubclass(raises, BaseException):
                        raise raises(e)
                    raise Exception(e)
                logger.error(f'[{func.__name__}] Unexpected error caught: {e}. Continuing...')
            return None
        return wrapper
    return decorator

# =================================
# Response models
# =================================

class ErrorMessage(BaseModel):
    error: str

# =================================
# Custom exceptions
# =================================

class BaseException(Exception):
    pass

class DeviceUnreachable(BaseException):
    pass

class UnexpectedSNMPPollError(BaseException):
    pass

class NoSNMPTrapSubscription(BaseException):
    pass

class InvalidInput(BaseException):
    pass

class InvalidInputType(InvalidInput):
    pass