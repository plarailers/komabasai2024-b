import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-8s]  %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(handler)
