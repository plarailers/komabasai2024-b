import asyncio
import platform

from bleak import BleakClient, BleakScanner

if platform.system() == "Windows":
    ADDRESS_E5 = "9c:9c:1f:cb:d9:f2"
    ADDRESS_E6 = "24:62:ab:e3:67:9a"
    ADDRESS_DR = "9c:9c:1f:cf:ea:de"
elif platform.system() == "Darwin":
    ADDRESS_E5 = "28652C68-A2CE-F0EF-93F1-857DCA3C7A4D"
    ADDRESS_E6 = "4BE5DF57-4E86-18DB-E792-C5D2F118610E"
    ADDRESS_DR = "9c:9c:1f:cf:ea:de"
else:
    raise Exception(f"{platform.system()} not supported")

SERVICE_UUID = "63cb613b-6562-4aa5-b602-030f103834a4"
CHARACTERISTIC_SPEED_UUID = "88c9d9ae-bd53-4ab3-9f42-b3547575a743"
CHARACTERISTIC_POSITIONID_UUID = "8bcd68d5-78ca-c1c3-d1ba-96d527ce8968"

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
        characteristicSpeed = service.get_characteristic(CHARACTERISTIC_SPEED_UUID)
        characteristicPositionId = service.get_characteristic(CHARACTERISTIC_POSITIONID_UUID)

        # await client.start_notify(characteristicPositionId, notification_callback)

        for i in range(100,200):
            await client.write_gatt_char(characteristic, f"{i}".encode())
            print("Wrote", i)
            await asyncio.sleep(1)

async def notification_callback(sender, data):
    # Notifyを受け取ったときの処理をここに記述
    print(f"Received data: {data}")
        
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
