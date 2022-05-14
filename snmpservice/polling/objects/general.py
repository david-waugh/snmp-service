from snmpservice.polling.objects.base import BasePollObject, snmp_get
from re import search

class HostName(BasePollObject):
    OID = ("1.3.6.1.2.1.1.5.0",)
    SNMP_CMD = snmp_get

    def parse(self, varbinds: list) -> dict:
        # Parse varbinds to find HostName
        for oid, value in varbinds:
            if any(oid == OID for OID in self.OID):
                # Value associated with self.OID = hostname.
                return dict(OID=oid, value=value)
        return dict(OID=None, value=None)

class DeviceModel(BasePollObject):
    OID = (
        "1.3.6.1.2.1.47.1.1.1.1.13.1", # Where Model should be
        "1.0.8802.1.1.2.1.3.4.0" # vMX workaround
    )
    SNMP_CMD = snmp_get
    JUNOS_MODEL_RGX = r"(?<=Juniper Networks, Inc\. )[a-zA-Z]+"

    def parse(self, varbinds: list) -> dict:
        # Parse the varbinds to find the OID + value 
        # pair that describes the DeviceModel
        model = None
        for varbind in varbinds:
            oid, value = varbind
            if oid == self.OID[0]:
                # Value is the model
                model = value
            elif oid == self.OID[1]:
                # Model should be found in the returned description string
                if (m := search(self.JUNOS_MODEL_RGX, value)): model = m.group(0)
        oid = oid if model else None
        return dict(OID=oid, value=model)

