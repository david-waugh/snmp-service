from pydantic import BaseSettings

# This isn't the best way of providing configuration for this service.
# Realistically, we should be parsing environment variables and using
# hardcoded defaults otherwise, as currently we rely on the user manually
# editing the source code (this bit specifically) to modify the operational
# settings of the snmp-service. 

# This does also require a re-install of the package to change the settings... oops. pip3 install .

class Settings(BaseSettings):
    # =================================
    # App Info
    # =================================
    app_name: str = "Visualisation snmp-service"
    app_contact_email: str = "david@dawaugh.co.uk"

    # =================================
    # SNMP Trap Server Config
    # =================================
    snmp_trap_ip: str = "127.0.0.1"
    snmp_trap_port: int = 162
    snmp_trap_community: str  = "public"
    snmp_trap_mib_modules: tuple = ('SNMPv2-MIB', 'SNMP-COMMUNITY-MIB', 'IF-MIB', 'LLDP-MIB')

    # =================================
    # SNMP Polling Mechanism Config
    # =================================
    snmp_poll_community: str = "visualisation"
    snmp_poll_strategy: str = "default"
    snmp_poll_port: int  = 161

    # =================================
    # Miscellaneous Config
    # =================================
    log_level: str  = "DEBUG"
    log_filename: str = "/tmp/dataservice.log"

settings = Settings()

