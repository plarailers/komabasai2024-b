import logging
from uuid import UUID

from bleak import BleakClient

from ptcs_control.components.junction import PointDirection

SERVICE_POINT_SWITCHING_UUID = UUID("2a4023a6-6079-efea-b79f-7c882319b83b")
CHARACTERISTIC_DIRECTION_UUID = UUID("737237f4-300e-ca58-1e2f-40ff59fc71f7")


def point_direction_to_command(direction: PointDirection) -> bytes:
    match direction:
        case PointDirection.STRAIGHT:
            return b"STRAIGHT"
        case PointDirection.CURVE:
            return b"CURVE"


logger = logging.getLogger(__name__)


class PointClient:
    id: str
    _client: BleakClient

    def __init__(self, id: str, address: str) -> None:
        self.id = id
        self._client = BleakClient(address)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id}, {self._client.address})"

    async def connect(self) -> None:
        await self._client.connect()
        logger.info("%s connected", self)

    async def disconnect(self) -> None:
        await self._client.disconnect()
        logger.info("%s disconnected", self)

    @property
    def is_connected(self) -> bool:
        return self._client.is_connected

    async def send_direction(self, direction: PointDirection) -> None:
        service = self._client.services.get_service(SERVICE_POINT_SWITCHING_UUID)
        assert service is not None
        characteristic = service.get_characteristic(CHARACTERISTIC_DIRECTION_UUID)
        assert characteristic is not None

        command = point_direction_to_command(direction)
        await self._client.write_gatt_char(characteristic, command, response=True)
        logger.info("%s send direction %s", self, command)
