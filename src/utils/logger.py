import logging

# To be imported by consuming modules
# __main__ should import setup_logger and execute if logging used.
logger = logging.getLogger(__name__)

def setup_logger(loglevel="INFO", filename=None):
    """
    Purpose:
        Initialise logger for robust message output.
    Inputs:
        loglevel : str : Choice of ("INFO", "DEBUG", "WARNING", "ERROR").
        filename : str : Filename for log file. Default=None (no storage).
    """
    if loglevel.upper() not in ("INFO", "DEBUG", "WARNING", "ERROR"):
        print(f'Invalid loglevel passed to setup_logger: {loglevel}. Falling back to INFO.')
        loglevel = "INFO"

    # Try to create log file. Lazy way.
    handlers = [logging.StreamHandler()]
    try:
        with open(filename, "a") as f:
            pass
        handlers.append(logging.FileHandler(filename))
    except PermissionError:
        pass

    # Setup logging
    logging.basicConfig(
        format='[%(threadName)s][%(module)s][%(funcName)s][%(levelname)s] %(message)s',
        datefmt='%I:%M:%S%p',
        encoding='utf-8', 
        level=loglevel,
        handlers=handlers
    )

if __name__ == "__main__":
    setup_logger()
