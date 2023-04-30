from ptcs_control.components import Train
from usb_bt_bridge.bridge import Bridge


BridgeDict = dict[Train, Bridge]


def create_bridges() -> BridgeDict:
    bridges: BridgeDict = {
        Train("t0"): Bridge("COM4"),
    }

    bridges[Train("t0")].send("hoge")

    return bridges
