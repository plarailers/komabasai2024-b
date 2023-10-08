import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)-8s]  %(message)s"))
logger.addHandler(handler)
