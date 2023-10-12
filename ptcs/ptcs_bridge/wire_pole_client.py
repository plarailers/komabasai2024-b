import logging
from typing import Callable
from uuid import UUID

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

NotifyCollapseCallback = Callable[["WirePoleClient", bool], None]


SERVICE_WIRE_POLE_UUID = UUID("62dd9b52-2995-7978-82e2-6abf1ae56555")
CHARACTERISTIC_COLLAPSE_UUID = UUID("79fe0b5c-754c-3fe0-941f-3dc191cf09bf")


logger = logging.getLogger(__name__)


class WirePoleClient:
    id: str
    _client: BleakClient

    def __init__(self, id: str, address: str) -> None:
        self.id = id
        self._client = BleakClient(address)

    def __str__(self) -> str:
        return f"WirePoleClient({self.id}, {self._client.address})"

    async def connect(self) -> None:
        await self._client.connect()
        logger.info("%s connected", self)

    async def disconnect(self) -> None:
        await self._client.disconnect()
        logger.info("%s disconnected", self)

    async def start_notify_collapse(self, callback: NotifyCollapseCallback) -> None:
        def wrapped_callback(_characteristic: BleakGATTCharacteristic, data: bytearray):
            assert len(data) == 1
            is_collapsed = bool(data[0])
            logger.info("%s notify collapse %s", self, is_collapsed)
            callback(self, is_collapsed)

        service = self._client.services.get_service(SERVICE_WIRE_POLE_UUID)
        assert service is not None
        characteristic = service.get_characteristic(CHARACTERISTIC_COLLAPSE_UUID)
        assert characteristic is not None

        await self._client.start_notify(characteristic, wrapped_callback)
