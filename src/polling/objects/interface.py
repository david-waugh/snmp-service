from snmpservice.polling.objects.base import BasePollObject, snmp_bulk_get
from pysnmp.hlapi import ObjectIdentity

class InterfacePollTask(BasePollObject):
    SNMP_CMD = snmp_bulk_get

    def extract_intf_index_from_oid(self, oid:ObjectIdentity, oid_index:int=-1) -> int | None:
        """
        Convenience method that attempts to get the interface
        index from the OID.

        Should be implemented by child-classes that deviate from
        the most common scenario implemented here.

        This scenario pulls the interface index from the last 
        value in the OID, e.g. 1.1.1.1.1.3 would return 3.
        """
        oid = tuple(oid) if isinstance(oid, ObjectIdentity) else oid
        if isinstance(oid, tuple):
            return int(oid[oid_index])
        elif isinstance(oid, str):
            return int(oid.split('.')[oid_index])
        return None

    def parse(self, varbinds: list) -> dict:
        response_varbinds = []
        for oid, value in varbinds:
            if any(oid.startswith(OID) for OID in self.OID):
                # Pull ifindex from OID.
                ifindex = self.extract_intf_index_from_oid(oid)
                response_varbinds.append(dict(OID=oid, value=value, IfIndex=ifindex))
        return [dict(OID=None, value=None)] if not response_varbinds else response_varbinds

class IfIndex(InterfacePollTask):
    OID = ("1.3.6.1.2.1.2.2.1.1",)

    def parse(self, varbinds: list) -> dict:
        # Parse varbinds to get IfIndex value
        response_varbinds = []
        for oid, ifindex in varbinds:
            if any(oid.startswith(OID) for OID in self.OID):
                response_varbinds.append(dict(OID=oid, value=ifindex, IfIndex=ifindex))
        return [dict(OID=None, value=None)] if not response_varbinds else response_varbinds

class IfName(InterfacePollTask):
    OID = ("1.3.6.1.2.1.31.1.1.1.1",)

class IfAdminStatus(InterfacePollTask):
    OID = ("1.3.6.1.2.1.2.2.1.7",)

    def parse(self, varbinds: list) -> dict:
        response_varbinds = []
        for oid, value in varbinds:
            if any(oid.startswith(OID) for OID in self.OID):
                value = "up" if value == 1 else "down"
                # Pull ifindex from OID.
                ifindex = self.extract_intf_index_from_oid(oid)
                response_varbinds.append(dict(OID=oid, value=value, IfIndex=ifindex))
        return [dict(OID=None, value=None)] if not response_varbinds else response_varbinds

class IfOperStatus(InterfacePollTask):
    OID = ("1.3.6.1.2.1.2.2.1.8",)

    def parse(self, varbinds: list) -> dict:
        response_varbinds = []
        for oid, value in varbinds:
            if any(oid.startswith(OID) for OID in self.OID):
                value = "up" if value == 1 else "down"
                # Pull ifindex from OID.
                ifindex = self.extract_intf_index_from_oid(oid)
                response_varbinds.append(dict(OID=oid, value=value, IfIndex=ifindex))
        return [dict(OID=None, value=None)] if not response_varbinds else response_varbinds

class IfDescr(InterfacePollTask):
    OID = ("1.3.6.1.2.1.2.2.1.2",)

class IfSpeed(InterfacePollTask):
    OID = ("1.3.6.1.2.1.31.1.1.1.15",)

class IfHCInOctets(InterfacePollTask):
    OID = ("1.3.6.1.2.1.31.1.1.1.6",)

class IfHCOutOctets(InterfacePollTask):
    OID = ("1.3.6.1.2.1.31.1.1.1.10",)
