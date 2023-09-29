from typing import Awaitable, Callable
from uuid import UUID

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTService

SERVICE_UUID = UUID("63cb613b-6562-4aa5-b602-030f103834a4")
CHARACTERISTIC_MOTOR_INPUT_UUID = UUID("88c9d9ae-bd53-4ab3-9f42-b3547575a743")
CHARACTERISTIC_POSITION_ID_UUID = UUID("8bcd68d5-78ca-c1c3-d1ba-96d527ce8968")
CHARACTERISTIC_ROTATION_UUID = UUID("aab17457-2755-8b50-caa1-432ff553d533")


class TrainClient:
    _client: BleakClient

    def __init__(self, address: str) -> None:
        self._client = BleakClient(address)

    async def connect(self) -> None:
        await self._client.connect()

    async def disconnect(self) -> None:
        await self._client.disconnect()

    def _get_service(self) -> BleakGATTService:
        service = self._client.services.get_service(SERVICE_UUID)
        assert service is not None
        return service

    def _get_characteristic(self, uuid: UUID) -> BleakGATTCharacteristic:
        service = self._get_service()
        characteristic = service.get_characteristic(uuid)
        assert characteristic is not None
        return characteristic

    def _get_characteristic_motor_input(self) -> BleakGATTCharacteristic:
        return self._get_characteristic(CHARACTERISTIC_MOTOR_INPUT_UUID)

    def _get_characteristic_position_id(self) -> BleakGATTCharacteristic:
        return self._get_characteristic(CHARACTERISTIC_POSITION_ID_UUID)

    def _get_characteristic_rotation(self) -> BleakGATTCharacteristic:
        return self._get_characteristic(CHARACTERISTIC_ROTATION_UUID)

    async def send_speed(self, speed: int) -> None:
        assert 0 <= speed <= 255
        characteristic_speed = self._get_characteristic_motor_input()
        await self._client.write_gatt_char(characteristic_speed, bytes([speed]))

    async def start_notify_position_id(
        self, callback: Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None] | None]
    ) -> None:
        characteristic_position_id = self._get_characteristic_position_id()
        await self._client.start_notify(characteristic_position_id, callback)

    async def start_notify_rotation(
        self, callback: Callable[[BleakGATTCharacteristic, bytearray], Awaitable[None] | None]
    ) -> None:
        characteristic_rotation = self._get_characteristic_rotation()
        await self._client.start_notify(characteristic_rotation, callback)
