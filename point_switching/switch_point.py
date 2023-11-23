import time
import asyncio
import platform

from bleak import BleakClient, BleakScanner

if platform.system() == "Windows":
    ADDRESS_POINT0 = '3C:71:BF:99:36:84'
    ADDRESS_POINT1 = '9c:9c:1f:cb:d9:f2'

elif platform.system() == "Darwin":
    ADDRESS_POINT0 = "9FA4916E-AD02-6C9C-686A-1B97D9E3427A"
    ADDRESS_POINT1 = "90386433-4331-50CF-1637-EFFA587DD6DB"

else:
    raise Exception(f"{platform.system()} not supported")

####### TODO: 車両のアドレスを指定してください #######
address = ADDRESS_POINT1
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