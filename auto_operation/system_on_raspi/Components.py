from enum import Enum


class Train:
    class MoveResult(Enum):
        No = 0
        PassedJunction = 1
        PassedStation = 2

    all = {}

    def __init__(self, id, initialSection: 'Section', initialPosition: float):
        self.id = 0
        self.targetSpeed = 0
        self.currentSection = initialSection
        self.mileage = initialPosition
        Train.all[id] = self

    # 返り値：現在の区間の何割のところにいるか [0, 1)
    def getPosition(self) -> float:
        position = self.mileage / self.currentSection.length
        return position

    # 引数：進んだ距離
    # 返り値：新しい区間に移ったかどうか
    def move(self, delta: float) -> MoveResult:
        prevMileage = self.mileage
        self.mileage += delta
        if (self.mileage >= self.currentSection.length):  # 分岐点を通過したとき
            self.mileage = self.mileage - self.currentSection.length
            self.currentSection = self.currentSection.targetJunction.getPointedSection()
            return Train.MoveResult.PassedJunction
        if self.currentSection.hasStation:
            stationPosition = self.currentSection.stationPosition
            if (prevMileage < stationPosition and stationPosition <= self.mileage):  # 駅を通過したとき
                return Train.MoveResult.PassedStation
        return Train.MoveResult.No

    @staticmethod
    def getById(id):
        return Train.all.get(id)


class Section:
    all = {}

    def __init__(self, id: int, sourceJunctionId: int, targetJunctionId: int, sourceServoState: 'Junction.ServoState', targetServoState: 'Junction.ServoState', length: float):
        self.id = id
        self.length = length
        self.sourceJunction = Junction.getById(sourceJunctionId)
        self.sourceJunction.addOutSection(self, sourceServoState)
        self.targetJunction = Junction.getById(targetJunctionId)
        self.targetJunction.addInSection(self, targetServoState)
        self.hasStation = False
        self.stationPosition = 0
        Section.all[id] = self

    def putStation(self, stationPosition):
        self.hasStation = True
        self.stationPosition = stationPosition

    @staticmethod
    def getById(id):
        return Section.all.get(id)  # 該当するSectionがないときはNoneが返る


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

    all = {}

    def __init__(self, id, servoId):
        self.id = id
        self.servoId = servoId
        self.inSectionStraight = None
        self.inSectionCurve = None
        self.outSectionStraight = None
        self.outSectionCurve = None
        self.inServoState = Junction.ServoState.Straight
        self.outServoState = Junction.ServoState.Straight
        Junction.all[id] = self

    def addInSection(self, section, servoState):
        if servoState == Junction.ServoState.Straight:
            self.inSectionStraight = section
        elif servoState == Junction.ServoState.Curve:
            self.inSectionCurve = section
        else:  # NoServoの時はStraight側に接続
            self.inSectionStraight = section
            self.inSectionCurve = None

    def addOutSection(self, section, servoState):
        if servoState == Junction.ServoState.Straight:
            self.outSectionStraight = section
        elif servoState == Junction.ServoState.Curve:
            self.outSectionCurve = section
        else:  # NoServoの時はStraight側に接続
            self.outSectionStraight = section
            self.outSectionCurve = None

    def toggle(self) -> ServoState:
        if self.inSectionStraight and self.inSectionCurve:  # IN側に2本入ってくる分岐点の場合
            self.inServoState = Junction.ServoState.invert(self.inServoState)  # 反転
            return Junction.ServoState.NoServo  # IN側分岐はサーボモータをつけないのでNoServoを返す
        elif self.outSectionStraight and self.outSectionCurve:  # OUT側に2本入ってくる分岐点の場合
            self.outServoState = Junction.ServoState.invert(self.outServoState)  # 反転
            return self.outServoState
        else:  # 分岐が無い場合
            return Junction.ServoState.NoServo

    def getPointedSection(self) -> Section:
        if self.outServoState == Junction.ServoState.Curve:
            return self.outSectionCurve
        else:
            return self.outSectionStraight

    def getInSection(self) -> Section:
        if self.inServoState == Junction.ServoState.Curve:
            return self.inSectionCurve
        else:
            return self.inSectionStraight

    @staticmethod
    def getById(id):
        return Junction.all.get(id)  # 該当するSectionがないときはNoneが返る


class Station:
    all = {}

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.trackDict = {}  # 番線とセクションを対応付けるdict
        Station.all[id] = self

    def setTrack(self, trackId, sectionId, stationPosition):
        Section.getById(sectionId).putStation(stationPosition)  # 駅の追加
        self.trackDict[trackId] = Section.getById(sectionId)  # 番線と紐づけ

    def getTrackIdBySection(self, section) -> int:
        for track in self.trackDict.values():
            if track.id == section.id:
                return track.id
        return 0

    @staticmethod
    def getBySection(section):
        for station in Station.all.values():
            for track in station.trackDict.values():
                if track.id == section.id:
                    return station
        return None

    @staticmethod
    def getById(id):
        return Station.all.get(id)


class Sensor:
    all = {}

    def __init__(self, id, belongSectionId, position):
        self.id = id
        self.belongSection = Section.getById(belongSectionId)
        self.position = position
        Sensor.all[id] = self

    @staticmethod
    def getById(id):
        return Sensor.all.get(id)


class StopPoint:  # 停止点情報
    def __init__(self, section: Section, mileage: float):
        self.section = section
        self.mileage = mileage
