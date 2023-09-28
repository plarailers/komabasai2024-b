import time
import asyncio
import platform

from bleak import BleakClient, BleakScanner

####### TODO: アドレスを正しく設定してください #######
if platform.system() == "Windows":
    ADDRESS_E5 = "7C:9E:BD:93:2E:72"
    ADDRESS_E6 = "24:62:ab:e3:67:9a"
    ADDRESS_DR = "9c:9c:1f:cf:ea:de"
elif platform.system() == "Darwin":
    ADDRESS_E5 = "28652C68-A2CE-F0EF-93F1-857DCA3C7A4D"
    ADDRESS_E6 = "4BE5DF57-4E86-18DB-E792-C5D2F118610E"
    ADDRESS_DR = "9c:9c:1f:cf:ea:de"
    ADDRESS_JT = "66D22FDC-6B41-36D0-BB07-C80BADA29DB2"
else:
    raise Exception(f"{platform.system()} not supported")

SERVICE_UUID = "63cb613b-6562-4aa5-b602-030f103834a4"
CHARACTERISTIC_SPEED_UUID = "88c9d9ae-bd53-4ab3-9f42-b3547575a743"
CHARACTERISTIC_POSITIONID_UUID = "8bcd68d5-78ca-c1c3-d1ba-96d527ce8968"
CHARACTERISTIC_ROTATION_UUID = "aab17457-2755-8b50-caa1-432ff553d533"

mileage_cm_ = 0.0

GEAR_RATIO = 175/8448
WHEEL_DIAMETER_cm_ = 2.4
PI = 3.14159265358979

async def main():
    print("Devices:")
    devices = await BleakScanner.discover()
    for d in devices:
        print("  - ", d)

    ####### TODO: クライアントのアドレスを選択してください #######
    async with BleakClient(ADDRESS_JT) as client:
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
        print(characteristicSpeed, characteristicPositionId, characteristicRotation)

        await client.start_notify(characteristicPositionId, positionIdNotification_callback)
        await client.start_notify(characteristicRotation, rotationNotification_callback)

        for i in range(100, 200):
            await client.write_gatt_char(characteristicSpeed, f"{i}".encode())
            print("motorInput:", i)
            await asyncio.sleep(1)
        

async def positionIdNotification_callback(sender, data):
    # positionId Notifyを受け取ったとき，positionIDを表示．mileageはリセット
    positionID = int.from_bytes(data, byteorder='big')
    print(f"positionID: {positionID}")
    mileage_cm_ = 0

async def rotationNotification_callback(sender, data):
    # rotation Notifyを受け取ったとき，mileageを車輪1/24回転分進める
    mileage_cm_ += WHEEL_DIAMETER_cm_ * PI / 24
    print(f"mileage: {mileage_cm_}")
    # 24ステップのロータリエンコーダをギアで1/2に減速するため12ステップで1回転とするのが妥当と思われるが，
    # ロータリエンコーダは左右の車輪に2つ搭載されており，左右のステップ数が合わせて24になったときに1回転とすることで，
    # カーブなど移動距離に左右差が生じる際に平均の移動距離を算出できる．
    # そのため，左右いずれかの1ステップを1/24回転として扱う．

loop = asyncio.get_event_loop()
loop.run_until_complete(main())