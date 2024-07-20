import logging
import sys

logger = logging.getLogger('fastapi')

formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')

# hangders
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
