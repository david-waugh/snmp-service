from snmpservice.utils.models.trapping import SubscriptionResponse
from snmpservice.trapping.store import trap_datastore
from snmpservice.utils.helpers import timestamp
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/subscription",
    tags=["Trap Subscription"]
)

@router.get('/{ip}',
    status_code = 200,
    responses = {
        200: {
            "description": "SNMP trap subscription exists.",
            "model": SubscriptionResponse
        },
        404: {
            "description": "SNMP trap subscription does not exist.", 
            "content": None
        },
    }
)
async def check_trap_subscription(ip:str) -> SubscriptionResponse | None:
    """Check if a trap subscription exists for given IP."""
    if await trap_datastore.has_subscription(ip):
        return SubscriptionResponse(
            IpAddress=ip, 
            Timestamp=timestamp(),
            Message=f'Subscription exists for IP "{ip}"'
        )
    raise HTTPException(404, detail=f'No subscription exists for IP "{ip}"')

@router.put('/{ip}', 
    status_code = 201,
    responses = {
        201: {
            "description": "SNMP trap subscription created successfully, or already existed.", 
            "model": SubscriptionResponse
        }
    }
)
async def create_trap_subscription(ip:str) -> SubscriptionResponse:
    """Create a trap subscription for given IP."""
    if await trap_datastore.create_subscription(ip):
        message = f'Subscription successfully created for IP "{ip}"'
    else:
        message = f'Subscription already exists for IP "{ip}"'
    return SubscriptionResponse(
        IpAddress=ip, 
        Timestamp=timestamp(), 
        Message=message
    )

@router.delete('/{ip}', 
    status_code = 200,
    responses = {
        200: {
            "description": "SNMP trap subscription deleted successfully.", 
            "model": SubscriptionResponse
        },
        404: {
            "description": "No subscription existent to delete."
        },
    }
)
async def delete_trap_subscription(ip:str) -> SubscriptionResponse | None:
    """Delete a trap subscription for given IP."""
    if await trap_datastore.delete_subscription(ip):
        return SubscriptionResponse(
            IpAddress=ip, 
            Timestamp=timestamp(), 
            Message=f'Subscription for IP "{ip}" successfully deleted.'
        )
    raise HTTPException(404, detail=f'No subscription exists for IP "{ip}"')
