from snmpservice.utils.models.polling import *
from snmpservice.utils.logger import logger
from snmpservice.utils.exceptions import *
from typing import Union, List, Tuple
from pysnmp.hlapi import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData, 
    ObjectIdentity, ObjectType, bulkCmd, getCmd
)

def snmp_get(_, community: CommunityData, target: UdpTransportTarget, oid: ObjectType) -> getCmd:
    """Creates an SNMP GET command generator."""
    return getCmd(SnmpEngine(), community, target, ContextData(), oid)

def snmp_bulk_get(_, community: CommunityData, target: UdpTransportTarget, oid: ObjectType) -> bulkCmd:
    """Creates an SNMP BULKGET command generator."""
    return bulkCmd(SnmpEngine(), community, target, ContextData(), 1, 5, oid, lexicographicMode=False)

def to_object_type(obj_identity: str | ObjectIdentity) -> ObjectType | None:
    """Given an OID string or ObjectIdentity, returns the corresponding ObjectType."""
    obj_identity = ObjectIdentity(obj_identity) if isinstance(obj_identity, str) else obj_identity
    return ObjectType(obj_identity) if isinstance(obj_identity, ObjectIdentity) else None

def extract_varbinds(cmd_gen: Union[getCmd, bulkCmd]) -> List[ObjectType]:
    """
    Extracts the list of varbinds from a getCmd or bulkCmd object.

    Positional arguments:
    cmd_gen : getCmd or bulkCmd : Command generator object.

    Returns:
    varbinds : list : List of non-errored varbind objects.
    """
    extracted_varbinds = []
    for err_indicator, err_status, err_index, varbinds in cmd_gen:
        if err_indicator:
            logger.error(f"[SNMP GET Error] {err_indicator}")
            raise DeviceUnreachable(f"Device is unreachable.")
        elif err_status and str(err_status) != "noError":
            logger.error(f"[SNMP GET Error] {err_status} at {err_index and varbinds[int(err_index) - 1][0] or '??'}")
        extracted_varbinds.extend(varbinds)
    return extracted_varbinds

def unpack_varbind(varbind: ObjectType) -> tuple:
    """
    Unpacks a varbind object (ObjectType) and returns the contained values.

    Positional arguments:
    varbind : ObjectType : Varbinds to unpack

    Returns:
    tuple : String (oid, value) pair, or (None, None) 
            if any values are errored or empty.

    Example varbind:
    ObjectType(
        ObjectIdentity(
            <ObjectName value object, tagSet <TagSet object, tags 0:0:6>, 
            payload [1.3.6.1.2.1.2.2.1.1.3]>
        ), 
        <Integer value object, 
            tagSet <TagSet object, tags 0:0:2>, 
            subtypeSpec <ConstraintsIntersection object, 
            consts <ValueRangeConstraint object, consts -2147483648, 2147483647>>, 
            payload [3]>
    )
    returns ("1.3.6.1.2.1.2.2.1.1.3", 3)
    """
    if isinstance(varbind, ObjectType):
        oid, value = varbind
        try:
            value = int(str(value))
        except ValueError:
            value = str(value)
        if isinstance(value, str) and (value.lower().startswith("no such") or value == ""):
            return None, None
        return str(oid), value
    return None, None

def extract_and_unpack_varbinds(cmd_gen: Union[getCmd, bulkCmd]) -> List[Tuple[str, str]]:
    """Calls extract_varbinds, followed by unpack_varbind for each varbind."""
    return [vb for varbind in extract_varbinds(cmd_gen) 
            if (vb := unpack_varbind(varbind)) != (None, None)]

class BasePollObject:
    """
    Object representing a single poll task, or a single SNMP GET/BULKGET command.

    Positional arguments:
    strategy : PollStrategy : PollStrategy-like instance that is calling the class.

    Properties:
    OID      : tuple  : SNMP OID that the class is responsible 
                        for retrieving and processing.
    SNMP_CMD : func   : SNMP command function from service.utils.snmp_operations
                        e.g. snmp_get or snmp_bulk_get
    
    Methods:
    retrieve   : Main method of the class, which should be used to 
                retrieve and parse data.
    """
    OID = (None,) 
    SNMP_CMD = None # snmp_get or snmp_bulk_get from this module

    def retrieve(self, target: UdpTransportTarget, community: CommunityData) -> dict | None:
        """
        Method to perform SNMP poll using self.OID, returning poll output.

        Positional arguments:
        target      : UdpTransportTarget : Target of OID poll.
        community   : CommunityData      : Community data for target.

        Returns:
        PollObjectResponse
        
        Raises:
        InvalidSNMPPollInputs  : Raised when inputs to function are invalid.
        UnexpectedSNMPPollError: Raised when an unexpected error has occured.
        DeviceUnreachable      : Raised when the poll request timeout occurs.
        """
        response = {"varbinds": []}
        for oid_index, oid in enumerate(self.OID):
            # Get the ObjectType object for self.OID
            oid_obj = to_object_type(oid)

            # Run SNMP CMD
            logger.debug(f"[{self.__class__.__name__}] Creating SNMP command gen...")
            cmd_gen = self.SNMP_CMD(community, target, oid_obj)
            if cmd_gen is None:
                logger.debug(f"[{self.__class__.__name__}] cmd_gen is None.")
                raise UnexpectedSNMPPollError(f"{self.__class__.__name__} cmd_gen is None")

            logger.debug(f"[{self.__class__.__name__}] Extracting and unpacking data...")
            try:
                varbinds = extract_and_unpack_varbinds(cmd_gen)
            except Exception as e:
                raise DeviceUnreachable(f"Device is unreachable. (Raw error: {type(e)} {e}")

            if not varbinds:
                # If there are more OIDs to try, continue. Else, fail.
                if oid_index < len(self.OID)-1:
                    continue
                logger.error(f'[{self.__class__.__name__}] Poll task failed to yield any varbinds.')
                return None

            logger.debug(f"[{self.__class__.__name__}] Parsing varbinds...")
            varbinds = self.parse(varbinds)

            # Add varbinds to response
            if isinstance(varbinds, (list, tuple)):
                for varbind in varbinds:
                    response["varbinds"].append(varbind)
            else:
                response["varbinds"].append(varbinds)
            break

        # Return data
        return response

    def parse(self, varbinds: list) -> dict:
        # To be implemented by child objects
        pass
