from snmpservice.utils.exceptions import *

from ipaddress import IPv4Address, AddressValueError
from datetime import datetime
from re import match

DATA_INTF_REGEX = r"^(((gigabit|fast)ethernet|gi|fa)[0-9]+(/[0-9]+)+)|((ge|et|xe)-[0-9]+(/[0-9]+)+)$"

def is_data_intf(intf_name:str) -> bool:
    """Is given intf_name a data interface? Matches against DATA_INTF_REGEX."""
    return match(DATA_INTF_REGEX, str(intf_name).lower())

def is_ipv4_address(val: str) -> bool:
    """Is 'val' a valid IPv4 address?"""
    try:
        IPv4Address(val)
    except AddressValueError:
        return False
    return True

def timestamp() -> int:
    """Returns integer epoch timestamp e.g. 1644590688"""
    return int(datetime.now().timestamp())
