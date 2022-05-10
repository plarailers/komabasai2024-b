from State import *
from DiaPlanner import *
from SignalSystem import *
from ATS import *
import time

# ダイヤ情報に基づく自動運転を行うクラス


class ATO:
    def __init__(self, state: State, signalSystem: SignalSystem, ats: ATS, diaPlanner: DiaPlanner) -> None:
        self.__ats = ats
        self.__signalSystem = signalSystem
        self.__state = state
        self.__diaPlanner = diaPlanner
        self.__prevUpdate = 0
        self.__enabled = {}  # 各列車の、ATO有効,無効が入る辞書. key=trainId, valued=enabled
        self.__arriveTime = {}  # 各列車が、直近に駅に到着した時刻を記録する辞書. key=trainId, value=float
        self.__maxSpeed = {}  # 各列車の最高速度
        for train in state.trainList:
            self.__enabled[train.id] = True
            self.__arriveTime[train.id] = 0
            self.__maxSpeed[train.id] = 0

    # 列車の出しうる最高速度を指定
    def setMaxSpeed(self, trainId: int, maxSpeed: int):
        self.__maxSpeed[trainId] = maxSpeed

    # ダイヤ情報をもとに、速度指令を自動的に更新する
    def update(self) -> None:
        now = time.time()
        dt = now - self.__prevUpdate
        self.__prevUpdate = now

        for train in self.__state.trainList:
            if self.__enabled[train.id]:
                # 停止位置をまたいだとき、駅に到着or通過したと判定し、arriveTimeを更新する
                if train.currentSection.station != None:
                    stationPosition = train.currentSection.stationPosition
                    if (train.prevMileage < stationPosition and stationPosition <= train.mileage):
                        self.__arriveTime[train.id] = now

                # 通過/停車に関わらずなんらかの駅に到着した後の場合
                if train.currentSection.station != None and train.mileage >= train.currentSection.stationPosition:
                    diaOfCurrentStation = self.__diaPlanner.getDia(train.id, train.currentSection.station.id)
                    stopDuration = time.time() - self.__arriveTime[train.id]  # 停車からの経過時間
                    departSignal = self.__signalSystem.getSignal(train.currentSection.id, train.currentSection.targetJunction.getOutSection().id)  # 出発信号機
                    # 到着した駅が退避駅でない & 最低停車時間を過ぎた & 信号が青 なら出発してよい
                    if diaOfCurrentStation.wait == False and stopDuration > diaOfCurrentStation.stopTime and departSignal.value == 'G':
                        speedCommand = min(train.targetSpeed + self.__maxSpeed[train.id]*dt/5, self.__maxSpeed[train.id])
                    # それ以外のときは出発しない
                    else:
                        speedCommand = 0

                # 駅到着より前の場合
                else:
                    # 次の停車駅を取得
                    nextStation = self.getNextStation(train)
                    diaOfNextStation = self.__diaPlanner.getDia(train.id, nextStation.id)
                    nextStationSection = self.__state.getSectionById(diaOfNextStation.arriveSectionId)
                    distanceToStation = self.__state.getDistance(train.currentSection, train.mileage, nextStationSection, nextStationSection.stationPosition)

                    # 通過の場合は最高速度
                    if diaOfNextStation.wait == False and diaOfNextStation.stopTime < 1:
                        speedCommand = self.__maxSpeed[train.id]
                    # 通過以外のとき、停止位置までの距離に応じて速度を適当に調整
                    else:
                        if distanceToStation > 100:
                            speedCommand = self.__maxSpeed[train.id]
                        elif distanceToStation > 0:
                            speedCommand = (0.9 * distanceToStation/100 + 0.1) * self.__maxSpeed[train.id]
                        else:
                            speedCommand = 0

                # 速度指令値を更新
                self.__ats.setSpeedCommand(train.id, speedCommand)

    # 列車を指定し、その列車の直近の停車駅を取得する(既に列車が駅に停車している場合はその駅を返す)
    def getNextStation(self, train: Train) -> Station:
        testSection = train.currentSection
        while True:
            # 現在のセクションに駅がある
            if testSection.station != None:
                stopTimeOnThisStation = self.__diaPlanner.getDia(train.id, testSection.station.id).stopTime
                # 当該駅で停車する
                if stopTimeOnThisStation > 1:
                    return testSection.station
            # 上記以外は次の駅へ
            testSection = testSection.targetJunction.getOutSection()

    # ATO無効の列車に対して、外部から速度を指令する
    def setInput(self, trainId: int, speedCommand: int) -> None:
        if not self.__enabled[trainId]:
            self.__ats.setSpeedCommand(trainId, speedCommand)

    # ATOの有効/無効を切り替える
    def setEnabled(self, trainId: int, enabled: bool):
        self.__enabled[trainId] = enabled
