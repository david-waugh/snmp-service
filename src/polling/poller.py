from snmpservice.polling.strategies import strategy_map
from snmpservice.utils.exceptions import *
from ipaddress import ip_address

from pysnmp.hlapi import UdpTransportTarget, CommunityData

def get_udp_transport_target(ip: str, port: int) -> UdpTransportTarget | None:
    """
    Produces a UdpTransportTarget object given an ip and port.

    Positional arguments:
    ip   : str : Target IP address
    port : int : Target remote port

    Returns:
    UdpTransportTarget object if the ip and port are of the correct type.
    None otherwise.
    """
    if (isinstance(ip, str) and isinstance(port, int)):
        try:
            ip_address(ip)
        except ValueError as e:
            raise InvalidInput(e)
        return UdpTransportTarget((ip, int(port)), timeout=5.0, retries=2)
    return None
            
def get_community_data(community_string: str) -> CommunityData | None:
    """
    Produces a CommunityData object given an SNMP community string.

    Positional arguments:
    community_string : str : SNMP community string.

    Returns:
    CommunityData object if the community_string is of the correct type.
    None otherwise.
    """
    if isinstance(community_string, CommunityData):
        return community_string
    if isinstance(community_string, str):
        return CommunityData(community_string)
    return None

def poll(ip: str, port: int, strategy: str, community: str) -> dict:
    """
    Function that, given a target IP address, will perform an SNMP poll following
    the strategy represented by the strategy string.

    Positional arguments:
    ip       : str : Target IP address to poll.
    port     : int : UDP port for the remote device.
    strategy : str : String representing the strategy class detailing
                      the poll specification. 
                      See service.poll.strategies.base
    community: str : SNMP community string to use.
    
    Returns:
    result : dict : Dictionary matching the structure defined by the poll strategy.

    Raises:
    DeviceUnreachable       : Target IP is unreachable on given port.
    InvalidInput            : One or more input(s) are of the invalid type or value.
    UnexpectedSNMPPollError : Unexpected error occured.
    """
    logger.debug(f"[POLL {ip}] Getting strategy for string '{strategy}'...")
    strategy = strategy_map.get(strategy, None)
    if strategy is None:
        raise InvalidInput(f"Unable to find strategy matching string '{strategy}'")

    # Build strategy inputs
    transport = get_udp_transport_target(ip, port)
    community = get_community_data(community)

    # Follow poll strategy
    try:
        return strategy().run(transport, community)
    except (DeviceUnreachable, InvalidInput):
        raise
    except Exception as e:
        raise UnexpectedSNMPPollError(e)
