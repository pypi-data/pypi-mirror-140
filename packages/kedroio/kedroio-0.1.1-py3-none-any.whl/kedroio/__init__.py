import logging

__version__ = "0.1.1"

logging.getLogger("kedro-io").addHandler(logging.NullHandler())
