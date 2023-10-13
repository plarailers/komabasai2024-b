import logging
from uuid import UUID

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.service import BleakGATTService

from .train_base import (
    NotifyPositionIdCallback,
    NotifyRotationCallback,
    NotifyVoltageCallback,
    TrainBase,
)

SERVICE_TRAIN_UUID = UUID("63cb613b-6562-4aa5-b602-030f103834a4")
CHARACTERISTIC_MOTOR_INPUT_UUID = UUID("88c9d9ae-bd53-4ab3-9f42-b3547575a743")
CHARACTERISTIC_POSITION_ID_UUID = UUID("8bcd68d5-78ca-c1c3-d1ba-96d527ce8968")
CHARACTERISTIC_ROTATION_UUID = UUID("aab17457-2755-8b50-caa1-432ff553d533")
CHARACTERISTIC_VOLTAGE_UUID = UUID("7ecc0ed2-5ef9-c9e6-5d16-582f86035ecf")


logger = logging.getLogger(__name__)


class TrainClient(TrainBase):
    id: str
    _client: BleakClient

    def __init__(self, id: str, address: str) -> None:
        self.id = id
        self._client = BleakClient(address)

    def __str__(self) -> str:
        return f"TrainClient({self.id}, {self._client.address})"

    async def connect(self) -> None:
        await self._client.connect()
        logger.info("%s connected", self)

    async def disconnect(self) -> None:
        await self._client.disconnect()
        logger.info("%s disconnected", self)

    @property
    def is_connected(self) -> bool:
        return self._client.is_connected

    def _get_service_train(self) -> BleakGATTService:
        service = self._client.services.get_service(SERVICE_TRAIN_UUID)
        assert service is not None
        return service

    def _get_characteristic(self, uuid: UUID) -> BleakGATTCharacteristic:
        service = self._get_service_train()
        characteristic = service.get_characteristic(uuid)
        assert characteristic is not None
        return characteristic

    def _get_characteristic_motor_input(self) -> BleakGATTCharacteristic:
        return self._get_characteristic(CHARACTERISTIC_MOTOR_INPUT_UUID)

    def _get_characteristic_position_id(self) -> BleakGATTCharacteristic:
        return self._get_characteristic(CHARACTERISTIC_POSITION_ID_UUID)

    def _get_characteristic_rotation(self) -> BleakGATTCharacteristic:
        return self._get_characteristic(CHARACTERISTIC_ROTATION_UUID)

    def _get_characteristic_voltage(self) -> BleakGATTCharacteristic:
        return self._get_characteristic(CHARACTERISTIC_VOLTAGE_UUID)

    async def send_motor_input(self, motor_input: int) -> None:
        assert isinstance(motor_input, int)
        assert 0 <= motor_input <= 255
        characteristic = self._get_characteristic_motor_input()
        await self._client.write_gatt_char(characteristic, f"{motor_input}".encode(), response=False)
        logger.info("%s send motor input %s", self, motor_input)

    async def start_notify_position_id(self, callback: NotifyPositionIdCallback) -> None:
        def wrapped_callback(_characteristic: BleakGATTCharacteristic, data: bytearray):
            assert len(data) == 1
            position_id = data[0]
            logger.info("%s notify position id %s", self, position_id)
            callback(self, position_id)

        characteristic = self._get_characteristic_position_id()
        await self._client.start_notify(characteristic, wrapped_callback)

    async def start_notify_rotation(self, callback: NotifyRotationCallback) -> None:
        def wrapped_callback(_characteristic: BleakGATTCharacteristic, data: bytearray):
            assert len(data) == 1
            assert data[0] == 1
            # logger.info("%s notify rotation %s", self, 1)
            callback(self, 1)

        characteristic = self._get_characteristic_rotation()
        await self._client.start_notify(characteristic, wrapped_callback)

    async def start_notify_voltage(self, callback: NotifyVoltageCallback) -> None:
        def wrapped_callback(_characteristic: BleakGATTCharacteristic, data: bytearray):
            assert len(data) == 4
            voltage = int.from_bytes(data, byteorder="little")
            logger.info("%s notify voltage %s mV", self, voltage)
            callback(self, voltage)

        characteristic = self._get_characteristic_voltage()
        await self._client.start_notify(characteristic, wrapped_callback)
