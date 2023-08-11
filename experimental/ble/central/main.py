import asyncio
from bleak import BleakScanner, BleakClient

ADDRESS_E5 = "9c:9c:1f:cb:d9:f2"
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"


async def main():
    print("Devices:")
    devices = await BleakScanner.discover()
    for d in devices:
        print("  - ", d)

    async with BleakClient(ADDRESS_E5) as client:
        print("Connected to", client)
        print("Services:")
        for service in client.services:
            print("  - ", service)
        service = client.services.get_service(SERVICE_UUID)
        print("Characteristics:")
        for characteristic in service.characteristics:
            print("  - ", characteristic)
        characteristic = service.get_characteristic(CHAR_UUID)

        for i in range(100):
            await client.write_gatt_char(characteristic, f"Hello {i}".encode())
            print("Wrote", i)
            await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
