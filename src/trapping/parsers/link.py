from snmpservice.trapping.parsers.base import BaseTrapParser
from snmpservice.utils.helpers import is_data_intf
from typing import Tuple

class LinkStateParser(BaseTrapParser):
    TRAP_NAME = "IntfStateChange"

    def _trap_parser(self, ip: str, trap_data: str) -> Tuple[str, dict]:
        # Get the state change trap, which tells us the action i.e. linkUp, linkDown
        change = trap_data.get("snmpTrapOID", None) 
    
        # Try to get interface name from ifName
        int_name = trap_data.get("ifName", None)
        # If we did not find the int name or change, ignore trap
        if not (int_name and change):
            return None

        # Check if interface is one we want to store traps for.
        if not is_data_intf(int_name):
            return None

        return int_name, dict(State=change, Interface=int_name)

# Human-readable OIDs of the traps that trigger this parser.
class linkUp(LinkStateParser):
    pass

class linkDown(LinkStateParser):
    pass
