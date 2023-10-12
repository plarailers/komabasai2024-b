from ptcs_bridge.bridge2 import Bridge2
from ptcs_bridge.train_client import TrainClient
from ptcs_bridge.train_simulator import TrainSimulator
from ptcs_bridge.wire_pole_client import WirePoleClient


def create_bridge() -> Bridge2:
    bridge = Bridge2()
    bridge.add_train(TrainSimulator("t0"))
    # bridge.add_train(TrainClient("t0", "e0:5a:1b:e2:7a:f2"))
    bridge.add_train(TrainSimulator("t1"))
    bridge.add_train(TrainSimulator("t2"))
    bridge.add_train(TrainSimulator("t3"))
    bridge.add_train(TrainSimulator("t4"))
    # bridge.add_obstacle(WirePoleClient("obstacle_0", "24:62:AB:E3:67:9A"))
    return bridge
