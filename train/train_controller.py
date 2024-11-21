import time
import asyncio
import platform

from bleak import BleakClient, BleakScanner

if platform.system() == "Windows":
    ADDRESS_T0 = "24:dc:c3:c0:4e:a6"
    ADDRESS_T1 = "48:E7:29:93:F4:B6"
    ADDRESS_T2 = "24:DC:C3:C0:3A:4E"
    ADDRESS_T3 = "48:E7:29:A0:FF:66"
    ADDRESS_T4 = "24:DC:C3:C0:51:7A"
    ADDRESS_T5 = "A0:B7:65:5C:1A:96"
    ADDRESS_T6 = "A0:B7:65:52:EF:5A"
    ADDRESS_T7 = "24:dc:c3:c0:51:72"
    ADDRESS_T8 = "48:e7:29:a1:07:ee"
    ADDRESS_T9 = "24:dc:c3:c0:49:92"
    ADDRESS_POINT0 = "3c:71:bf:99:36:86"
    ADDRESS_POINT1 = "9c:9c:1f:cb:d9:f2"
    ADDRESS_POINT2 = "08:3a:8d:14:7a:0e"
    ADDRESS_POINT3 = "08:b6:1f:ee:3f:d6"
    ADDRESS_POINT4 = "0c:b8:15:78:41:b2"
    ADDRESS_POINT5 = "7c:9e:bd:93:2e:72"
    ADDRESS_POINT6 = "24:62:ab:e3:67:9a"
    ADDRESS_POINT7 = "9c:9c:1f:d1:68:26"
    ADDRESS_POINT8 = "fc:f5:c4:1a:3b:3a"

elif platform.system() == "Darwin":
    ADDRESS_T0 = "F8EE254B-DBB8-5C62-367B-C045E11DE9C4"
    ADDRESS_T1 = "8EE8710E-C17B-7B8F-2EE3-1E0FDE0243C5"
    ADDRESS_T2 = "9F1478BB-8FB4-BF30-6DC2-F4861F9719E7"
    ADDRESS_T3 = "10556715-D1EE-98BD-BE81-7C783BBC1405"
    ADDRESS_T4 = "B287A4B7-3567-1CE8-2E94-0428003D353C"
    ADDRESS_T5 = "1276ADDC-6E7C-011D-2584-5D0F51459A8A"
    ADDRESS_T6 = "9D5FCACE-1EFE-F9D1-4643-9B15ED0881D3"
    ADDRESS_T7 = "E7D2BF5C-331F-9FDE-B2EF-47CB507A69CB"
    ADDRESS_T8 = "2B59D30D-F1E0-E4F7-9056-67E74D182F76"
    ADDRESS_T9 = "E61E694E-7D52-1BD1-5B7A-02402813E73E"
    ADDRESS_POINT0 = "9FA4916E-AD02-6C9C-686A-1B97D9E3427A"
    ADDRESS_POINT1 = "90386433-4331-50CF-1637-EFFA587DD6DB"
    ADDRESS_POINT2 = "2E4CD350-F39B-03B1-295C-F98C728C15E4"
    ADDRESS_POINT3 = "5365F30F-2457-DC22-903E-37C81D6DF486"
    ADDRESS_POINT4 = "872E54C6-24D2-7E32-A123-9CA81C5AB8D7"
    ADDRESS_POINT5 = "28652C68-A2CE-F0EF-93F1-857DCA3C7A4D"
    ADDRESS_POINT6 = "4BE5DF57-4E86-18DB-E792-C5D2F118610E"
    ADDRESS_POINT7 = "3D6ABB53-D496-8379-3274-4134F840D7D8"
    ADDRESS_POINT8 = "A6343D14-C836-2D3C-738F-BAC596B918CF"

else:
    raise Exception(f"{platform.system()} not supported")

####### TODO: 車両のアドレスを指定してください #######
address = ADDRESS_T9
#################################################

SERVICE_UUID = "63cb613b-6562-4aa5-b602-030f103834a4"
CHARACTERISTIC_SPEED_UUID = "88c9d9ae-bd53-4ab3-9f42-b3547575a743"
CHARACTERISTIC_POSITIONID_UUID = "8bcd68d5-78ca-c1c3-d1ba-96d527ce8968"
CHARACTERISTIC_ROTATION_UUID = "aab17457-2755-8b50-caa1-432ff553d533"
CHARACTERISTIC_VOLTAGE_UUID = "7ecc0ed2-5ef9-c9e6-5d16-582f86035ecf"

mileage_cm_ = 0.0
newtime = 0.0
oldtime = 0.0
WHEEL_DIAMETER_cm_ = 2.4
PI = 3.14159265358979

# テストコース(直線2本と曲線8本)
STRAIGHT_RAIL_cm_ = 21.50
CURVE_RAIL_cm_ = 16.90
COURSE_LENGTH_cm_ = STRAIGHT_RAIL_cm_ * 2 + CURVE_RAIL_cm_ * 8

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
                    i = 220
                elif address == ADDRESS_T1:
                    i = 200
                elif address == ADDRESS_T2:
                    i = 220
                elif address == ADDRESS_T3:
                    i = 170
                elif address == ADDRESS_T4:
                    i = 210
                elif address == ADDRESS_T5:
                    i = 160
                elif address == ADDRESS_T6:
                    i = 222
                elif address == ADDRESS_T7:
                    i = 220
                elif address == ADDRESS_T8:
                    i = 225
                elif address == ADDRESS_T9:
                    i = 222

                while True:
                    await client.write_gatt_char(characteristicSpeed, f"{i}".encode())
                    print("motorInput:", i)
                    await asyncio.sleep(0.3)
        except:
            print("disconnected")
        

async def positionIdNotification_callback(sender, data):
    # positionId Notifyを受け取ったとき，positionIDを表示．mileageはリセット
    global mileage_cm_
    global newtime
    global oldtime
    positionID = hex(int.from_bytes(data, byteorder='big'))
    print(f"positionID: {positionID}")

    # テストコースにRFIDカード1枚配置してスピードを計測。30 cm/sくらいがRFIDを読み取る上でちょうどいい
    oldtime = newtime
    newtime = time.time()
    print(f"speed (cm/s): {COURSE_LENGTH_cm_ / (newtime - oldtime)}")
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