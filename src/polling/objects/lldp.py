from snmpservice.polling.objects.interface import InterfacePollTask, snmp_bulk_get

class LldpPollTask(InterfacePollTask):
    SNMP_CMD = snmp_bulk_get

    def parse(self, varbinds: list) -> dict:
        # Parse varbinds to get remote hostname.
        response_varbinds = []
        print(self.__class__.__name__, varbinds)
        for oid, value in varbinds:
            if any(oid.startswith(OID) for OID in self.OID):
                # Pull ifindex from OID
                ifindex = self.extract_intf_index_from_oid(oid, oid_index=-2)
                response_varbinds.append(dict(OID=oid, value=value, IfIndex=ifindex))
        return [dict(OID=None, value=None)] if not response_varbinds else response_varbinds

class LldpRemHost(LldpPollTask):
    OID = ("1.0.8802.1.1.2.1.4.1.1.9",)

class LldpRemPort(LldpPollTask):
    OID = ("1.0.8802.1.1.2.1.4.1.1.7",)

class LldpRemHostIpAddr(LldpPollTask):
    OID = ("1.0.8802.1.1.2.1.4.2.1.4.0",)

    def parse(self, varbinds: list) -> dict:
        # Parse varbinds to get remote host IP address.
        response_varbinds = []
        print(varbinds)
        for oid, value in varbinds:
            if any(oid.startswith(OID) for OID in self.OID):
                # OID = ...{intf_index}.x.x.x.{ip_address} Value = ifindex
                ip_addr = '.'.join(oid.split('.')[-4:])
                ifindex = self.extract_intf_index_from_oid(oid, oid_index=-8)
                response_varbinds.append(dict(OID=oid, value=ip_addr, IfIndex=ifindex))
        return [dict(OID=None, value=None)] if not response_varbinds else response_varbinds
