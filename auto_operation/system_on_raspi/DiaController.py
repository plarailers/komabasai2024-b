from State import *


class DiaController:
    def __init__(self, state: State):
        self.__state = state
        self.__autoToggle = True  # 自動種別設定の有効/無効
        self.__passageFlag = {}  # 追い抜きフラグ(Trueで追い抜き、Falseで退避)
        for train in self.__state.trainList:  # trainIdから追い抜きフラグを引く辞書を作る
            self.__passageFlag[train.id] = False
        
        self.__prevMileage = 0  # 直前の列車位置を記録しておく場所
        self.__nowMileage = 0

    # 種別自動切り替えのルールを記述. 毎update時によぶ
    def update(self) -> None:
        # 今回は、train[0]が退避駅を出発し、次のセクションに入ったあたりのタイミングで、train0と1のフラグを反転させる
        TRAIN_ID = 0
        SECTION_ID = 4
        SECTION_MILEAGE = 20
        train0 = self.__state.getTrainById(TRAIN_ID)
        self.__prevMileage = self.__nowMileage
        self.__nowMileage = train0.mileage
        if train0.currentSection.id == SECTION_ID:
            if self.__prevMileage < SECTION_MILEAGE and SECTION_MILEAGE < self.__nowMileage:
                self.__passageFlag[0] = not self.__passageFlag[0]
                self.__passageFlag[1] = not self.__passageFlag[1]

    # 引数 列車id
    # 返り値 指定した列車の追い抜きフラグ(True:追い抜き/False:退避)
    def getPassageFlag(self, trainId: int) -> bool:
        return self.__passageFlag[trainId]

    # 列車idに対する追い抜きフラグ(追い抜き/退避)を外から設定(手動モード時のみ有効)
    def setPassageFlag(self, trainId: int, flag: bool) -> None:
        if not self.__autoToggle:
            self.__passageFlag[trainId] = flag

    # 種別自動切り替えを有効/無効化
    def setAutoToggleEnabled(self, enabled: bool) -> None:
        self.__autoToggle = enabled
