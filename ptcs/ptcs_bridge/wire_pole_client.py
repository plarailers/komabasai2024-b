import logging
from typing import Callable
from uuid import UUID

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from .util import retry_connect

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
        logger.info("%s start notify collapse", self)

        # 倒れたり起き上がったりした瞬間にしか notify が来ないので、
        # 起動時にこちらから状態を読み取る
        data = await self._client.read_gatt_char(characteristic)
        wrapped_callback(characteristic, data)
        logger.info("%s read collapse %s", self, data)
