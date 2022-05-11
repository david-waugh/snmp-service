from snmpservice.utils.exceptions import NoSNMPTrapSubscription
from snmpservice.utils.models.trapping import Trap
from snmpservice.utils.logger import logger
from threading import Lock

class TrapDatastore:
    """
    Object representing a dictionary datastore for storing and accessing 
    SNMP traps in a shared memory space.

    Methods:
    create_subscription : Create SNMP trap subscription for device.
    check_subscription  : Checks whether a device has an SNMP trap subscription.
    delete_subscription : Deletes SNMP trap subscription for device.
    get_traps           : Get all stored SNMP traps for a given device.
    store_trap          : Store an SNMP trap for a given device.
    """
    def __init__(self):
        self._data = {}
        self._lock = Lock()
    
    async def create_subscription(self, ip:str) -> bool:
        """
        Creates SNMP trap subscription for device with ip.

        Positional arguments:
        ip : str : Device identifier. E.g. an IP address or hostname.

        Returns:
        True if subscription created.
        None if subscription already exists.
        """
        # If device already has subscription, return a None value.
        if str(ip) not in self._data:
            # Create a lock on the data to prevent race conditions.
            with self._lock:
                logger.debug(f"Creating subscription for {ip}.")
                self._data[str(ip)] = []
            return True
        return False
    
    async def has_subscription(self, ip:str) -> bool:
        """Returns true/false for whether device has subscription."""
        return bool(str(ip) in self._data)

    async def delete_subscription(self, ip:str) -> bool:
        """
        Deletes SNMP trap subscription for device with ip.

        Positional arguments:
        ip : str : Device identifier. E.g. an IP address or hostname.

        Returns:
        True if subscription created.
        None if subscription already exists.
        """
        if str(ip) in self._data:
            # Create a lock on the data to prevent race conditions.
            with self._lock:
                logger.debug(f"Deleting subscription for {ip}.")
                self._data.pop(str(ip))
            return True
        return False

    async def get_traps(self, device_id:str) -> dict | None:
        """
        Retrieves stored SNMP traps for device with device_id.

        Positional arguments:
        device_id : str : ID for device.

        Returns:
        traps : dict : Dictionary of all stored traps for device_id.
                       Key = trap names, Values = trap data.
        OR
        None if no device subscription created.

        Raises:
        NoSNMPTrapSubscription if no SNMP trap subscription exists for device.
        """
        # Check if subscription exists for device
        if str(device_id) not in self._data:
            raise NoSNMPTrapSubscription()
        # Create a lock on the data to prevent race conditions.
        with self._lock:
            # Retrieve traps for device, if any.
            traps = self._data.get(str(device_id), False)
        return traps
    
    async def store_trap(self, ip: str, new_trap: Trap) -> bool:
        """
        Stores a passed SNMP trap for device with device_id.

        Positional arguments:
        ip       : str   : ID for device.
        new_trap : Trap  : Parsed trap to store

        Returns:
        true if the trap is stored. false if no device subscription active.
        """
        logger.debug(f"Adding trap {new_trap} to datastore for device {ip}.")
        if ip in self._data:
            for index, trap in enumerate(self._data[ip]):
                if new_trap.TrapId == trap.TrapId:
                    with self._lock:
                        self._data[ip][index] = new_trap
                        return True
            with self._lock:
                self._data[ip].append(new_trap)
                return True
        return False

trap_datastore = TrapDatastore()