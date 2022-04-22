from enum import Enum
import string


class Section:
    def __init__(self, id: int, sourceJunction: 'Junction', targetJunction: 'Junction', sourceServoState: 'Junction.ServoState', targetServoState: 'Junction.ServoState', length: float):
        self.id = id
        self.length = length
        self.station = None
        self.stationPosition = 0
        self.sourceJunction = sourceJunction
        self.sourceJunction.addOutSection(self, sourceServoState)
        self.targetJunction = targetJunction
        self.targetJunction.addInSection(self, targetServoState)

    def putStation(self, station: 'Station', stationPosition: float):
        self.station = station
        self.stationPosition = stationPosition


class Junction:
    class ServoState(Enum):
        NoServo = 0
        Straight = 1
        Curve = 2

        @staticmethod
        def invert(input: 'Junction.ServoState'):
            if input == Junction.ServoState.Straight:
                return Junction.ServoState.Curve
            elif input == Junction.ServoState.Curve:
                return Junction.ServoState.Straight
            else:
                return Junction.ServoState.NoServo

    def __init__(self, id: int, servoId: int):
        self.id = id
        self.servoId = servoId
        self.inSectionStraight = None
        self.inSectionCurve = None
        self.outSectionStraight = None
        self.outSectionCurve = None
        self.inServoState = Junction.ServoState.Straight
        self.outServoState = Junction.ServoState.Straight
        self.belongStation = None

    def addInSection(self, section, servoState):
        if servoState == Junction.ServoState.Straight:
            self.inSectionStraight = section
        elif servoState == Junction.ServoState.Curve:
            self.inSectionCurve = section
        else:  # NoServoの時はStraight側に接続
            self.inSectionStraight = section
            self.inSectionCurve = None
            self.inServoState = Junction.ServoState.NoServo

    def addOutSection(self, section, servoState):
        if servoState == Junction.ServoState.Straight:
            self.outSectionStraight = section
        elif servoState == Junction.ServoState.Curve:
            self.outSectionCurve = section
        else:  # NoServoの時はStraight側に接続
            self.outSectionStraight = section
            self.outSectionCurve = None
            self.outServoState = Junction.ServoState.NoServo

    def toggle(self):
        if self.inSectionStraight and self.inSectionCurve:  # IN側に2本入ってくる分岐点の場合
            self.inServoState = Junction.ServoState.invert(self.inServoState)  # 反転
        elif self.outSectionStraight and self.outSectionCurve:  # OUT側に2本入ってくる分岐点の場合
            self.outServoState = Junction.ServoState.invert(self.outServoState)  # 反転

    def setServoState(self, servoState: ServoState):
        if self.inSectionStraight and self.inSectionCurve:  # IN側に2本入ってくる分岐点の場合inServoStateをセット
            self.inServoState = servoState
        if self.outSectionStraight and self.outSectionCurve:  # OUT側に2本入ってくる分岐点の場合outServoStateをセット
            self.outServoState = servoState

    def getOutSection(self) -> Section:
        if self.outServoState == Junction.ServoState.Curve:
            return self.outSectionCurve
        else:
            return self.outSectionStraight

    def getInSection(self) -> Section:
        if self.inServoState == Junction.ServoState.Curve:
            return self.inSectionCurve
        else:
            return self.inSectionStraight


class Sensor:
    def __init__(self, id: int, belongSection: Section, position: float):
        self.id = id
        self.belongSection = belongSection
        self.position = position


class Station:
    def __init__(self, id: int, name: string):
        self.id = id
        self.name = name


class Train:
    class MoveResult(Enum):
        No = 0
        PassedJunction = 1
        PassedStation = 2

    def __init__(self, id: int, initialSection: Section, initialPosition: float):
        self.id = id
        self.targetSpeed = 0
        self.currentSection = initialSection
        self.mileage = initialPosition

    # 引数：進んだ距離
    # 返り値：新しい区間に移ったかどうか
    def move(self, delta: float) -> MoveResult:
        prevMileage = self.mileage
        self.mileage += delta
        if (self.mileage >= self.currentSection.length):  # 分岐点を通過したとき
            self.mileage = self.mileage - self.currentSection.length
            self.currentSection = self.currentSection.targetJunction.getOutSection()
            return Train.MoveResult.PassedJunction
        if self.currentSection.hasStation:
            stationPosition = self.currentSection.stationPosition
            if (prevMileage < stationPosition and stationPosition <= self.mileage):  # 駅を通過したとき
                return Train.MoveResult.PassedStation
        return Train.MoveResult.No
