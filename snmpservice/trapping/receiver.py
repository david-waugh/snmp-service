from snmpservice.utils.logger import logger
from snmpservice.settings import settings
from snmpservice.trapping.store import trap_datastore
from snmpservice.trapping.parsers import get_parser_for_trap

from pysnmp.smi import builder, view, rfc1902
from pysnmp.entity import config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.hlapi import SnmpEngine

from threading import Thread

# 
# NOTE: For this to function correctly, you must 
# pip3 install pysnmp-mibs
#

def dispatch_trap_receiver(*, ip: str, port: int, community: str):
    """
    Spawns a daemon thread listening on given ip/port for SNMP traps using given community.

    Positional arguments:
    ip        : str : Ip address to listen for traps on.
    port      : int : Port to listen for traps on.
    community : str : SNMPv1/2c community string.
    """

    def _callback(
            snmp_engine:SnmpEngine, 
            state_reference:int, 
            context_engine_id, 
            context_name, 
            var_binds, 
            callback_context:None
        ) -> None:
        def numeric_to_lexical_oid(oid) -> str:
            """
            Attempts to translate OID to the human-friendly representation.
            e.g. 1.3.6.1.2.1.1.2 -> sysObjectID
            """
            try:
                return str(rfc1902.ObjectIdentity(oid).resolveWithMib(mib_view_controller).getLabel()[-1])
            except Exception as e:
                return str(oid)

        """Callback function to process recieved SNMP trap notifications."""
        trap = {}

        # Pull sender's IP address from the execution context
        exec_context = snmp_engine.observer.getExecutionContext('rfc3412.receiveMessage:request')
        peer_address, _ = exec_context["transportAddress"]

        logger.debug(f"Recieved SNMP notification from {peer_address}")
        # Translate numeric OIDs to human-friendly textual OIDs
        for name, val in var_binds:
            trap[numeric_to_lexical_oid(name)] = numeric_to_lexical_oid(val)
        
        # Parse desired information from the trap, if applicable, and store it.
        parser = get_parser_for_trap(trap.get("snmpTrapOID"))
        if parser:
            parsed_trap_data = parser().parse(peer_address, trap) 
            if parsed_trap_data:
                return trap_datastore.store_trap(peer_address, parsed_trap_data)

        # No data stored.
        return None

    def _dispatch():
        try:
            logger.info("Running trap receiver dispatcher...")
            ntfrcv.NotificationReceiver(snmp_engine, _callback)
            snmp_engine.transportDispatcher.jobStarted(1)
            snmp_engine.transportDispatcher.runDispatcher()
        finally:
            snmp_engine.transportDispatcher.closeDispatcher()

    global mib_view_controller
    global snmp_engine
    snmp_engine = SnmpEngine()
    
    logger.info(f'Initialising TrapEngine with vars:\n'
                f'| IP: {ip}\n| Port: {port}\n'
                f'| Community: {community}\n'
                f'| SNMP Engine ID: {id(snmp_engine)}')

    logger.debug(f'[TrapEngine] MIB Modules: {settings.snmp_trap_mib_modules}')
    mib_builder = builder.MibBuilder()
    mib_view_controller = view.MibViewController(mib_builder)
    mib_builder.loadModules(*settings.snmp_trap_mib_modules)


    # Setup UDP transport
    config.addTransport(
        snmp_engine,
        udp.domainName + (1,),
        udp.UdpTransport().openServerMode((ip, port))
    )
    
    config.addV1System(snmp_engine, 'snmp-service', community)
    Thread(target=_dispatch, daemon=True).start()
