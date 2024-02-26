import logging

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "app.log"

# Get the root logger
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

# Clear existing handlers
logger.handlers = []

# Create file handler which logs even debug messages
fh = logging.FileHandler(LOG_FILE, mode="w")
fh.setLevel(LOG_LEVEL)
fh.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(fh)  # Add the file handler to the root logger

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
ch.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(ch)  # Add the stream handler to the root logger
