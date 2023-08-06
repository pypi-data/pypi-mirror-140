import logging
import sys


logging.basicConfig(stream=sys.stdout, filemode="w", level=logging.ERROR)

logger = logging.getLogger()
