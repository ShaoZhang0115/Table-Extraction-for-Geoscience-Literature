import logging

from .settings import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL.upper(), format="%(asctime)-15s [%(levelname)s] [%(name)-9s] %(message)s")
