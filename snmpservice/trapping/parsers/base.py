from snmpservice.utils.logger import logger
from snmpservice.utils.helpers import timestamp
from snmpservice.utils.models.trapping import Trap
from typing import Tuple

class BaseTrapParser:
    """
    Object providing trap-specific parsing capabilities.

    Usage:
    parsed_trap = TrapParser.parse(ip, trap_data)
    """
    TRAP_NAME = None
    
    def parse(self, ip:str, trap_data:dict) -> Trap:
        """
        Function to parse incoming SNMP traps using the subclass-implemented
        _trap_parser function, and to return the output in a structured format.

        Positional arguments:
        ip        : str : IP address of which the SNMP trap originates from.
        trap_data : dict : Dictionary containing trap data.

        Returns:
        Dictionary with trap data if trap parsing succeeds. None otherwise.

        Example:
        Trap(
            TrapId = "IntfStateChange_ge-0/0/0",
            IpAddress = "192.168.0.1",
            Timestamp = 1644590688,
            TrapName = "IntfStateChange",
            TrapData": {
                "State": "linkDown",
                "Interface": "ge-0/0/0"
            }
        )
        """
        try:
            id_suffix, trap_data = self._trap_parser(ip, trap_data)
        except Exception as e:
            logger.error(f'Trap parser {self.__class__.__name__} raised error {e}')
            trap_data = None

        if not trap_data: return None
        
        return Trap(
            TrapId=f"{self.TRAP_NAME}_{id_suffix}",
            IpAddress=ip,
            Timestamp=timestamp(),
            TrapName=self.TRAP_NAME,
            TrapData=trap_data
        )
    
    def _trap_parser(self, ip: str, trap_data: dict) -> Tuple[str, dict]:
        # To be implemented by subclasses
        # Must return 2 values
        # id_suffix : str  : suffix to be appended to TrapName to form
        #                    a unique trap name for a single device
        # trap_data : dict : trap-specific data dictionary
        pass