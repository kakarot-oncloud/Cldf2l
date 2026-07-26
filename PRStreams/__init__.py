import time
import logging

__version__ = "1.0.0"
StartTime = time.time()

logging.basicConfig(
    level=logging.INFO,
    datefmt="%d-%b-%y %H:%M:%S",
    format="[%(asctime)s][%(levelname)s] %(name)s :: %(message)s",
    handlers=[logging.StreamHandler()],
)

# Quiet down the very chatty third party loggers.
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

LOGGER = logging.getLogger("PRStreams")
