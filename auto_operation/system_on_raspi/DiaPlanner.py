from State import *

# ダイヤを管理、更新する
# Diaクラスの意味:
#   { trainId: 0,
#     stationId: 0,
#     wait: False,
#     stopTime: 10,
#     arriveSectionId: 2,
#     destSectionId: 4 }
#   -> 列車0は駅1で最低0秒停車=通過. section2に到着しsection4へ出発
#   { trainId: 1,
#     stationId: 1,
#     wait: True,
#     stopTime: 10,
#     arriveSectionId: 3,
#     destSectionId: 4 }
#   -> 列車1は駅1で退避. 最低10秒停車. section3に到着しsection4へ出発


class Dia:
    def __init__(self, trainId: int, stationId: int, wait: bool, stopTime: int, arriveSectionId: int, destSectionId: int):
        self.trainId = trainId
        self.stationId = stationId
        self.wait = wait
        self.stopTime = stopTime
        self.arriveSectionId = arriveSectionId
        self.destSectionId = destSectionId


class DiaPlanner:
    def __init__(self, state: State):
        self.__state = state
        self.__autoUpdate = True  # 自動更新の有効/無効
        self.__diaList: list[Dia] = []  # ダイヤリスト
        for train in self.__state.trainList:  # trainIdとstationIdからダイヤリストを生成
            for station in self.__state.stationList:
                self.__diaList.append(Dia(train.id, station.id, False, 10, 0, 0))

        self.__prevDistance = 0  # 直前の列車位置を記録しておく場所
        self.__nowDistance = 0

    # ダイヤ自動更新の初期値を記述
    def setup(self) -> None:
        # 今回は、列車0を追い抜き、列車1を退避として初期値をセット
        self.setDia(0, 0, False, 10, 0, 1)
        self.setDia(1, 0, False, 10, 0, 1)
        self.setDia(0, 1, False, 0, 2, 4)
        self.setDia(1, 1, True, 10, 3, 4)

    # ダイヤ自動更新のルールを記述. 毎update時によぶ
    def update(self) -> None:
        # 今回は、列車0と1の順序が入れ替わった(退避に成功した)タイミングで、train0と1の退避フラグを反転させる
        # 順序が入れ替わったことは、列車0から見た列車1までの距離が非連続に大きく変化したタイミングで検知する
        if self.__autoUpdate:
            train0 = self.__state.getTrainById(0)
            train1 = self.__state.getTrainById(1)
            self.__prevDistance = self.__nowDistance
            self.__nowDistance = self.__state.getDistance(train0.currentSection, train0.mileage, train1.currentSection, train1.mileage)
            if abs(self.__nowDistance - self.__prevDistance) > 100:
                if self.getDia(0, 1).wait == True:  # 列車0は直前まで退避していた
                    self.setDia(0, 1, False, 0, 2, 4)  # 列車0を追い抜きに
                    self.setDia(1, 1, True, 10, 3, 4)  # 列車1を退避に
                else:
                    self.setDia(0, 1, True, 10, 3, 4)
                    self.setDia(1, 1, False, 0, 2, 4)

    # 指定した列車の、指定した駅に対するダイヤを取得
    def getDia(self, trainId: int, stationId: int) -> Dia:
        result = list(filter(lambda x: (x.trainId == trainId and x.stationId == stationId), self.__diaList))
        return result[0]

    # 指定した列車の、指定した駅に対するダイヤを更新
    def setDia(self, trainId: int, staionId: int, wait: bool, stopTime: int, arriveSectionId: int, destSectionId: int) -> None:
        for dia in self.__diaList:
            if dia.trainId == trainId and dia.stationId == staionId:
                dia.wait = wait
                dia.stopTime = stopTime
                dia.arriveSectionId = arriveSectionId
                dia.destSectionId = destSectionId
                break

    # ダイヤ自動更新を有効/無効化
    def setAutoUpdateEnabled(self, enabled: bool) -> None:
        self.__autoUpdate = enabled
