from snmpservice.trapping.parsers.base import BaseTrapParser
from snmpservice.trapping.parsers.link import *
from inspect import isclass

def get_parser_for_trap(trap: str) -> BaseTrapParser | None:
    """
    Iterates over globals to find derived classes of BaseTrapParser
    and checks if any match name of given 'trap' variable. 

    Returns class if found, else None.
    """
    for var in globals().values():
        if isclass(var) and issubclass(var, BaseTrapParser):
            if var.__name__.lower() == trap.lower():
                return var
    return None