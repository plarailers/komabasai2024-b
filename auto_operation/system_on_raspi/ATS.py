from Components import *
from State import *
from SignalSystem import *


class ATS:
    # STOPMERGINで最高速度における制動距離を指定
    def __init__(self, state: State, signalSystem: SignalSystem, STOPMERGIN: float):
        self.__state = state
        self.__signalSystem = signalSystem
        self.__STOPMERGIN = STOPMERGIN
        self.__enabled = {}  # 各列車の、ATO有効,無効が入る辞書. key=trainId, valued=enabled
        for train in state.trainList:
            self.__enabled[train.id] = True

    # 指定した列車に対して速度を指令する. このとき、衝突しないような速度に変えて送信する
    def setSpeedCommand(self, trainId: int, speedCommand: float):
        if self.__enabled[trainId]:
            train = self.__state.getTrainById(trainId)
            signal = self.__signalSystem.getSignal(train.currentSection.id, train.currentSection.targetJunction.getOutSection().id)
            if signal.value == 'R':  # 赤信号の場合、制動距離を越えたら速度を0にする
                distance = self.__state.getDistance(train.currentSection, train.mileage, train.currentSection, train.currentSection.length)
                if distance < self.__STOPMERGIN:
                    train.targetSpeed = 0
                    return
        train.targetSpeed = speedCommand

    # ATSの有効/無効を切替
    def setEnabled(self, trainId: int, enabled: bool):
        self.__enabled[trainId] = enabled
