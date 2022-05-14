from pydantic import BaseModel
from typing import List

####### Trap Models #######

class Trap(BaseModel):
    TrapId: str
    IpAddress: str
    Timestamp: int
    TrapName: str
    TrapData: dict

####### API Endpoint Response Models #######

class GetTrapsResponse(BaseModel):
    Timestamp: int
    Traps: List[Trap] = []
    
class SubscriptionResponse(BaseModel):
    IpAddress: str
    Timestamp: int
    Message: str
