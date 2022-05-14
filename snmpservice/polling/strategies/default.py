from snmpservice.utils.helpers import is_data_intf, timestamp
from snmpservice.utils.models.polling import *
from snmpservice.polling.objects import *

from pysnmp.hlapi import UdpTransportTarget, CommunityData
from typing import List

### Strategy data models

class DefaultStrategyLldpModel(BaseStrategyModel):
    LldpRemHost: str | None
    LldpRemHostIpAddr: str | None
    LldpRemPort: str | None

class DefaultStrategyInterfaceModel(BaseStrategyModel):
    IfIndex: int
    IfAdminStatus: str | None
    IfOperStatus: str | None
    IfName: str | None
    IfDescr: str | None
    IfSpeed: int | None
    IfHCInOctets: int | None
    IfHCOutOctets: int | None
    Neighbour: DefaultStrategyLldpModel = DefaultStrategyLldpModel()

class DefaultStrategyModel(BaseStrategyModel):
    Timestamp: int
    IpAddress: str
    HostName: str | None
    DeviceModel: str | None
    Interfaces: List[DefaultStrategyInterfaceModel] = []

### Strategy

class DefaultPollStrategy:
    POLL_OBJECTS = (
        # Sys objects
        HostName,
        DeviceModel,

        # Interface objects
        IfIndex,
        IfName,
        IfDescr,
        IfAdminStatus,
        IfOperStatus,
        IfSpeed,
        IfHCInOctets,
        IfHCOutOctets,

        # LLDP objects
        LldpRemHost,
        LldpRemHostIpAddr,
        LldpRemPort
    )

    def _get_interface(self, model: DefaultStrategyModel, ifindex: int) -> BaseStrategyModel:
        # Gets interface with given ifindex. If it does not exist, creates it.
        for if_model in model.Interfaces:
            if if_model.IfIndex == int(ifindex):
                return if_model

        # To get to this stage, no such interface exists. Create it.
        if_model = DefaultStrategyInterfaceModel(IfIndex = ifindex)
        model.Interfaces.append(if_model)
        return if_model

    def run(self, target: UdpTransportTarget, community: CommunityData) -> dict:
        """Run SNMP polling strategy."""
        model = DefaultStrategyModel(Timestamp=timestamp(), IpAddress=target.transportAddr[0])

        for poll_object in self.POLL_OBJECTS: 
            # Get SNMP OID varbind(s).
            poll_object_response = poll_object().retrieve(target, community)
            if not isinstance(poll_object_response, dict):
                continue

            # Process retrieved SNMP OID varbind(s).
            obj_name = poll_object.__name__
            for varbind in poll_object_response.get("varbinds", []):
                if varbind.get("value") == None: continue
                if varbind.get("IfIndex"):
                    intf_model = self._get_interface(model, varbind.get("IfIndex"))
                    if obj_name.lower().startswith("lldp"):
                        intf_model.Neighbour[obj_name] = varbind["value"]
                    else:
                        intf_model[obj_name] = varbind["value"]
                else:
                    model[obj_name] = varbind["value"]

        model.Interfaces = [
            interface for interface in model.Interfaces
            if is_data_intf(interface.IfName)
        ]
        return model.dict()
