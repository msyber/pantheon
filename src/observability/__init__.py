import sys

from loguru import logger

# It's good practice to remove the default handler to avoid duplicate messages
# if the module is imported multiple times in a complex setup.
# The default loguru logger has a handler for stderr, so we remove it first.
logger.remove()

# Configure Loguru to write to a file and to the console
log_file_path = "logs/app.log"

logger.add(log_file_path, rotation="10 MB", retention="7 days", level="DEBUG")
logger.add(sys.stderr, level="CRITICAL", format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

# The logger is now configured and can be imported directly from this module.
