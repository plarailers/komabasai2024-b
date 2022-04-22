from State import *
from Components import *

# 列車の通過中など、ポイントを切り替えてはいけないときに切り替わらないよう制御する
class PointInterlock:
    def __init__(self, state: State, TRAIN_LENGTH: float):
        self.__state = state
        self.__TRAIN_LENGTH = TRAIN_LENGTH

    # ポイントを切り替える
    def requestToggle(self, junctionId: int):
        junction = self.__state.getJunctionById(junctionId)
        trainOnJunction = self.__state.getTrainInSection(junction.getOutSection())
        if trainOnJunction == None or trainOnJunction.mileage > self.__TRAIN_LENGTH:
            junction.toggle()
            