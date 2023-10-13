import time
import asyncio
import platform

from bleak import BleakClient, BleakScanner

if platform.system() == "Windows":
    ADDRESS_T0 = 'e0:5a:1b:e2:7a:f2'
    ADDRESS_T1 = '94:b5:55:84:15:42'
    ADDRESS_T2 = 'e0:5a:1b:e2:7b:1e'
    ADDRESS_T3 = '1c:9d:c2:66:84:32'
    ADDRESS_T4 = '24:4c:ab:f5:c6:3e'


elif platform.system() == "Darwin":
    ADDRESS_T0 = "00B55AE6-34AA-23C2-8C7B-8C11E6998E12"
    ADDRESS_T1 = "F2158243-18BB-D34C-88BC-F8F193CAD15E"
    ADDRESS_T2 = 'EB57E065-90A0-B6D0-98BA-81096FA5765E'
    ADDRESS_T3 = '4AA3AAE5-A039-8484-013C-32AD94F50BE0'
    ADDRESS_T4 = 'FC44FB3F-CF7D-084C-EA29-7AFD10C47A57'

else:
    raise Exception(f"{platform.system()} not supported")

####### TODO: 車両のアドレスを指定してください #######
address = ADDRESS_T4
#################################################

SERVICE_UUID = "63cb613b-6562-4aa5-b602-030f103834a4"
CHARACTERISTIC_SPEED_UUID = "88c9d9ae-bd53-4ab3-9f42-b3547575a743"
CHARACTERISTIC_POSITIONID_UUID = "8bcd68d5-78ca-c1c3-d1ba-96d527ce8968"
CHARACTERISTIC_ROTATION_UUID = "aab17457-2755-8b50-caa1-432ff553d533"
CHARACTERISTIC_VOLTAGE_UUID = "7ecc0ed2-5ef9-c9e6-5d16-582f86035ecf"

mileage_cm_ = 0.0

WHEEL_DIAMETER_cm_ = 2.4
PI = 3.14159265358979

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
                characteristicSpeed = service.get_characteristic(CHARACTERISTIC_SPEED_UUID)
                characteristicPositionId = service.get_characteristic(CHARACTERISTIC_POSITIONID_UUID)
                characteristicRotation = service.get_characteristic(CHARACTERISTIC_ROTATION_UUID)
                characteristicVoltage = service.get_characteristic(CHARACTERISTIC_VOLTAGE_UUID)
                print(characteristicSpeed, characteristicPositionId, characteristicRotation, characteristicVoltage)

                await client.start_notify(characteristicPositionId, positionIdNotification_callback)
                await client.start_notify(characteristicRotation, rotationNotification_callback)
                await client.start_notify(characteristicVoltage, voltageNotification_callback)

                if address == ADDRESS_T0:
                    i = 230
                elif address == ADDRESS_T1:
                    i = 200
                elif address == ADDRESS_T2:
                    i = 210
                elif address == ADDRESS_T3:
                    i = 220
                elif address == ADDRESS_T4:
                    i = 230

                while True:
                    await client.write_gatt_char(characteristicSpeed, f"{i}".encode())
                    print("motorInput:", i)
                    await asyncio.sleep(0.3)
        except:
            print("disconnected")
        

async def positionIdNotification_callback(sender, data):
    # positionId Notifyを受け取ったとき，positionIDを表示．mileageはリセット
    global mileage_cm_
    positionID = int.from_bytes(data, byteorder='big')
    print(f"positionID: {positionID}")
    mileage_cm_ = 0

async def rotationNotification_callback(sender, data):
    # rotation Notifyを受け取ったとき，mileageを車輪1/24回転分進める
    global mileage_cm_
    mileage_cm_ += WHEEL_DIAMETER_cm_ * PI / 24
    print(f"mileage: {mileage_cm_}")
    # 24ステップのロータリエンコーダをギアで1/2に減速するため12ステップで1回転とするのが妥当と思われるが，
    # ロータリエンコーダは左右の車輪に2つ搭載されており，左右のステップ数が合わせて24になったときに1回転とすることで，
    # カーブなど移動距離に左右差が生じる際に平均の移動距離を算出できる．
    # そのため，左右いずれかの1ステップを1/24回転として扱う．

async def voltageNotification_callback(sender, data):
    # voltage Notifyを受け取ったとき，voltageを表示．
    voltage = int.from_bytes(data, byteorder='little')
    print(f"Vin: {voltage} mV")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())