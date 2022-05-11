from snmpservice.utils.models.polling import DefaultStrategyModel
from snmpservice.utils.exceptions import *
from snmpservice.settings import settings
from snmpservice.utils.logger import logger
from snmpservice.utils.helpers import is_ipv4_address
from snmpservice.polling.poller import poll

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/poll",
    tags=["poll"],
    responses = {
        200: {
            "description": "Poll succeeded. DefaultStrategyModel encoded in payload.",
            "model": DefaultStrategyModel
        },
        460: {
            "description": "SNMP inputs are invalid.",
        },
        461: {
            "description": "Target device is unreachable, misconfigured, or uses a different SNMP community string.",
        }
    }
)

@router.get('/{ip}')
def default_poll_endpoint(ip: str, port: int = settings.snmp_poll_port, community: str = settings.snmp_poll_community) -> DefaultStrategyModel:
    """Request an SNMP poll on the device with IP passed in URI path."""
    try:
        # Validate inputs
        if is_ipv4_address(ip) == False:
            raise InvalidInput("'ip' input must be a valid IP address.")
        if not isinstance(port, int) or (isinstance(port, str) and not port.isnumeric()):
            raise InvalidInput("'port' input must be an integer.")
        
        logger.debug(f"Performing SNMP poll with vars:"
                    f"\n| IP: {ip}"
                    f"\n| Port: {port}"
                    f"\n| Community: {community}"
        )
        poll_response = poll(ip=ip, port=int(port), community=community, strategy="default")
        print(poll_response)
    except InvalidInput as e:
        raise HTTPException(status_code = 460, detail = f"Invalid Input: {e}")
    except DeviceUnreachable as e:
        raise HTTPException(status_code = 461, detail = f"Device Unreachable.")
    return poll_response
