from ATO import *
from ATS import *
from DiaPlanner import *
from PointInterlock import *
from PointSwitcher import *
from SignalSystem import *
from State import *


class Operation:
    STOPMERGIN = 20
    TRAIN_LENGTH = 30

    def __init__(self) -> None:
        self.state = State()
        self.diaPlanner = DiaPlanner(self.state)
        self.signalSystem = SignalSystem(self.state)
        self.ats = ATS(self.state, self.signalSystem, Operation.STOPMERGIN)
        self.pointInterlock = PointInterlock(self.state, Operation.TRAIN_LENGTH)
        self.pointSwitcher = PointSwitcher(self.state, self.diaPlanner, self.pointInterlock)
        self.ato = ATO(self.state, self.ats, self.diaPlanner)
    
    def update(self) -> None: 
        self.state.update()  # 現実世界のデバイスから状態を取得
        self.diaPlanner.update()  # 各列車のダイヤ(通過/退避など)を更新
        self.pointSwitcher.update()  # ダイヤに従ってポイント切り替え
        self.ato.update()  # ダイヤに従って列車の速度を更新
        self.state.sendCommand()  # 現実世界のデバイスに指令を送信

