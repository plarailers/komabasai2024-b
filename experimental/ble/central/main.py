import asyncio
from bleak import BleakScanner, BleakClient

ADDRESS_E5 = "9c:9c:1f:cb:d9:f2"
SERVICE_UUID = "63cb613b-6562-4aa5-b602-030f103834a4"
CHARACTERISTIC_UUID = "88c9d9ae-bd53-4ab3-9f42-b3547575a743"


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
        characteristic = service.get_characteristic(CHARACTERISTIC_UUID)

        for i in range(100):
            await client.write_gatt_char(characteristic, f"Hello {i}".encode())
            print("Wrote", i)
            await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
