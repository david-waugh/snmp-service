from snmpservice.utils.models.trapping import GetTrapsResponse
from snmpservice.trapping.store import trap_datastore
from snmpservice.utils.helpers import timestamp
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/traps",
    tags=["traps"],
    responses = {
        200: {
            "description": "Succesfully retrieved stored SNMP traps.",
            "model": GetTrapsResponse
        },
        404: {
            "description": "Subscription does not exist for IP. Create subscription and try again."
        }
    }
)

@router.get('/{ip}')
async def get_traps_endpoint(ip:str) -> GetTrapsResponse | None:
    """
    Retrieve the stored SNMP traps for device with IP. 
    Will not auto-create a trap subscription if one does not exist.
    """
    if await trap_datastore.has_subscription(ip):
        return GetTrapsResponse(Traps=await trap_datastore.get_traps(ip), Timestamp=timestamp())
    raise HTTPException(404, detail=f'No subscription exists for IP "{ip}"')