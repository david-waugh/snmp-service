from snmpservice.trapping.store import trap_datastore
from snmpservice.trapping.receiver import dispatch_trap_receiver
from snmpservice.utils.logger import logger, setup_logger
from snmpservice.utils.exceptions import *
from snmpservice.settings import settings
from snmpservice.routes import poll, subscribe, traps

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from os import _exit

app = FastAPI(
    title="Visualisation DataService",
    docs_url="/docs", redoc_url=None
)

app.include_router(poll.router)
app.include_router(subscribe.router)
app.include_router(traps.router)

@app.on_event('startup')
def setup():
    """Sets up the logger and dispatches a daemon thread for SNMP trap reception."""
    setup_logger(
        loglevel=settings.log_level, 
        filename=settings.log_filename
    )
    logger.info("Logger setup complete.")
    try:
        logger.info("Initialising trap receiver...")
        dispatch_trap_receiver(
            ip = settings.snmp_trap_ip,
            port = settings.snmp_trap_port,
            community = settings.snmp_trap_community,
        )
    except Exception as e:
        logger.critical(f"Initialisation failure. Error: {e}")
        _exit(0) # Hacky way to make multi-threaded process terminate.
    logger.info("TrapEngine setup complete.")


@app.get('/debug')
def debug_endpoint():
    """Dump the trap datastore for debugging."""
    logger.debug("Getting raw datastore.")
    return {"data": trap_datastore._data}

@app.get('/ping', responses={200:{"content":{"text/plain":{"example":"pong"}}}}, response_class=PlainTextResponse)
def ping_endpoint():
    """Test connectivity with data service."""
    return "pong"
