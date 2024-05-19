import time
import asyncio
import platform

from bleak import BleakClient, BleakScanner

if platform.system() == "Windows":
    ADDRESS_POINT0 = '3c:71:bf:99:36:86'
    ADDRESS_POINT1 = '9c:9c:1f:cb:d9:f2'
    ADDRESS_POINT2 = '08:3a:8d:14:7a:0e'
    ADDRESS_POINT3 = '08:b6:1f:ee:3f:d6'
    ADDRESS_POINT4 = '0c:b8:15:78:41:b2'
    ADDRESS_POINT5 = '7c:9e:bd:93:2e:72'
    ADDRESS_POINT6 = '24:62:ab:e3:67:9a'
    ADDRESS_POINT7 = '9c:9c:1f:d1:68:26'

elif platform.system() == "Darwin":
    ADDRESS_POINT0 = "9FA4916E-AD02-6C9C-686A-1B97D9E3427A"
    ADDRESS_POINT1 = "90386433-4331-50CF-1637-EFFA587DD6DB"
    ADDRESS_POINT2 = "2E4CD350-F39B-03B1-295C-F98C728C15E4"
    ADDRESS_POINT3 = "5365F30F-2457-DC22-903E-37C81D6DF486"
    ADDRESS_POINT4 = "872E54C6-24D2-7E32-A123-9CA81C5AB8D7"
    ADDRESS_POINT5 = "28652C68-A2CE-F0EF-93F1-857DCA3C7A4D"
    ADDRESS_POINT6 = "4BE5DF57-4E86-18DB-E792-C5D2F118610E"
    ADDRESS_POINT7 = "3D6ABB53-D496-8379-3274-4134F840D7D8"

else:
    raise Exception(f"{platform.system()} not supported")

####### TODO: 車両のアドレスを指定してください #######
address = ADDRESS_POINT4
#################################################

SERVICE_UUID = "2a4023a6-6079-efea-b79f-7c882319b83b"
CHARACTERISTIC_DIRECTION_UUID = "737237f4-300e-ca58-1e2f-40ff59fc71f7"

async def main():
    print("Devices:")
    devices = await BleakScanner.discover()
    for d in devices:
        print("  - ", d)

    while True:
        try:
            async with BleakClient(address) as client:
                print("Connected to", client)
                print("Services:")
                for service in client.services:
                    print("  - ", service)
                service = client.services.get_service(SERVICE_UUID)
                print("Characteristics:")
                for characteristic in service.characteristics:
                    print("  - ", characteristic)
                characteristicDirection = service.get_characteristic(CHARACTERISTIC_DIRECTION_UUID)
                print(characteristicDirection)

                while True:
                    direction = "STRAIGHT"
                    await client.write_gatt_char(characteristicDirection, f"{direction}".encode())
                    print("Direction: ", direction)
                    await asyncio.sleep(1)

                    direction = "CURVE"
                    await client.write_gatt_char(characteristicDirection, f"{direction}".encode())
                    print("Direction: ", direction)
                    await asyncio.sleep(1)
        except Exception as e:
            print("disconnected", e)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())