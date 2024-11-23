import platform

from ptcs_bridge.bridge2 import Bridge2
from ptcs_bridge.master_controller_client import MasterControllerClient
from ptcs_bridge.point_client import PointClient
from ptcs_bridge.train_client import TrainClient
from ptcs_bridge.train_simulator import TrainSimulator

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
    ADDRESS_MASTER_CONTROLLER = "9c:9c:1f:cf:ea:de"
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
    ADDRESS_MASTER_CONTROLLER = "E538DF32-E46A-3177-8196-3B9A8D4861A9"
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


def create_bridge() -> Bridge2:
    bridge = Bridge2()

    # bridge.add_train(TrainSimulator("t0"))
    bridge.add_train(TrainClient("t0", ADDRESS_T0))
    # bridge.add_train(TrainSimulator("t1"))
    # bridge.add_train(TrainClient("t1", ADDRESS_T1))
    # bridge.add_train(TrainSimulator("t2"))
    # bridge.add_train(TrainClient("t2", ADDRESS_T2))
    # bridge.add_train(TrainSimulator("t3"))
    bridge.add_train(TrainClient("t3", ADDRESS_T3))
    # bridge.add_train(TrainSimulator("t4"))
    # bridge.add_train(TrainClient("t4", ADDRESS_T4))
    # bridge.add_train(TrainSimulator("t5"))
    bridge.add_train(TrainClient("t5", ADDRESS_T5))
    # bridge.add_train(TrainSimulator("t6"))
    bridge.add_train(TrainClient("t6", ADDRESS_T6))
    # bridge.add_train(TrainSimulator("t7"))
    bridge.add_train(TrainClient("t7", ADDRESS_T7))
    # bridge.add_train(TrainSimulator("t8"))
    bridge.add_train(TrainClient("t8", ADDRESS_T8))
    # bridge.add_train(TrainSimulator("t9"))
    bridge.add_train(TrainClient("t9", ADDRESS_T9))
    bridge.add_controller(MasterControllerClient("t8", ADDRESS_MASTER_CONTROLLER))
    bridge.add_point(PointClient("j142", ADDRESS_POINT1))
    bridge.add_point(PointClient("j168", ADDRESS_POINT2))
    bridge.add_point(PointClient("j146", ADDRESS_POINT3))

    return bridge
