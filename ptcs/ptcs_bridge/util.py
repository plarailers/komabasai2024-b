import logging
from typing import Any

from bleak import BleakClient
from bleak.exc import BleakDeviceNotFoundError

logger = logging.getLogger(__name__)


async def retry_connect(client: BleakClient, obj: Any, trial: int = 3):
    count = 0
    while True:
        count += 1
        try:
            await client.connect()
            break
        except BleakDeviceNotFoundError as e:
            if count <= trial:
                logger.info(f"{obj} connection failed ({count}). Try again...")
            else:
                raise e
