import logging
from typing import Callable
from uuid import UUID

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from .util import retry_connect

NotifySpeedCallback = Callable[["MasterControllerClient", int], None]


SERVICE_MASTER_CONTROLLER_UUID = UUID("cea8c671-fb2c-5f3c-87ea-7ddea950b9a5")
CHARACTERISTIC_SPEED_UUID = UUID("4bb36d3a-dace-c0e6-e70c-81e0e77930cb")


logger = logging.getLogger(__name__)


class MasterControllerClient:
    id: str
    _client: BleakClient

    def __init__(self, id: str, address: str) -> None:
        self.id = id
        self._client = BleakClient(address)

    def __str__(self) -> str:
        return f"MasterControllerClient({self.id}, {self._client.address})"

    async def connect(self) -> None:
        await retry_connect(self._client, self)
        logger.info("%s connected", self)

    async def disconnect(self) -> None:
        if self._client.is_connected:
            await self._client.disconnect()
            logger.info("%s disconnected", self)
        else:
            logger.info("%s tried to disconnect, but not connected", self)

    @property
    def is_connected(self) -> bool:
        return self._client.is_connected

    async def start_notify_speed(self, callback: NotifySpeedCallback) -> None:
        def wrapped_callback(_characteristic: BleakGATTCharacteristic, data: bytearray):
            assert len(data) == 4
            speed = data[0]
            logger.info("%s notify speed %s", self, speed)
            callback(self, speed)

        service = self._client.services.get_service(SERVICE_MASTER_CONTROLLER_UUID)
        assert service is not None
        characteristic = service.get_characteristic(CHARACTERISTIC_SPEED_UUID)
        assert characteristic is not None

        await self._client.start_notify(characteristic, wrapped_callback)
        logger.info("%s start notify speed", self)
