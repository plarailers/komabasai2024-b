import asyncio
import platform

from bleak import BleakClient, BleakScanner

if platform.system() == "Windows":
    ADDRESS_E5 = "9c:9c:1f:cb:d9:f2"
    ADDRESS_E6 = "24:62:ab:e3:67:9a"
    ADDRESS_DR = "9c:9c:1f:cf:ea:de"
elif platform.system() == "Darwin":
    ADDRESS_E5 = "90386433-4331-50CF-1637-EFFA587DD6DB"
    ADDRESS_E6 = "4BE5DF57-4E86-18DB-E792-C5D2F118610E"
    ADDRESS_DR = "9c:9c:1f:cf:ea:de"
else:
    raise Exception(f"{platform.system()} not supported")

SERVICE_UUID = "63cb613b-6562-4aa5-b602-030f103834a4"
CHARACTERISTIC_UUID = "88c9d9ae-bd53-4ab3-9f42-b3547575a743"


async def main():
    print("Devices:")
    devices = await BleakScanner.discover()
    for d in devices:
        print("  - ", d)

    async with BleakClient(ADDRESS_E6) as client:
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
