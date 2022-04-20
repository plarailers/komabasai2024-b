from turtle import st
from Components import *


class State:
    STRAIGHT_UNIT = 21.5  # 直線レールの長さ[cm]
    CURVE_UNIT = 16.9  # 曲線レールの長さ[cm]

    junctionList = []
    sectionList = []
    trainList = []
    stationList = []
    sensorList = []

    # __init__で線路形状と車両の配置を定義する
    def __init__(self):
        # Junction(id, servoId)
        self.junctionList.append(Junction(0, -1))
        self.junctionList.append(Junction(1, 1))
        self.junctionList.append(Junction(2, 0))
        self.junctionList.append(Junction(3, -1))

        # Section(id, length, sourceId, targetId, sourceServoState)
        self.sectionList.append(Section(0, 3, 0, Junction.ServoState.NoServo, Junction.ServoState.NoServo, State.STRAIGHT_UNIT * 5.5))
        self.sectionList.append(Section(1, 0, 1, Junction.ServoState.NoServo, Junction.ServoState.NoServo, State.STRAIGHT_UNIT * 5 + State.CURVE_UNIT * 4))
        self.sectionList.append(Section(2, 1, 2, Junction.ServoState.Straight, Junction.ServoState.Straight, State.STRAIGHT_UNIT * 5.5))
        self.sectionList.append(Section(3, 1, 2, Junction.ServoState.Curve, Junction.ServoState.Curve, State.STRAIGHT_UNIT * 5.5))
        self.sectionList.append(Section(4, 2, 3, Junction.ServoState.NoServo, Junction.ServoState.NoServo, State.STRAIGHT_UNIT * 3 + State.CURVE_UNIT * 4))
        # 場合によっては、初回の着発番線に合わせてここにtoggleを挟む必要がある

        # Sensor(id, sectionId, position)
        self.sensorList.append(Sensor(0, 1, State.STRAIGHT_UNIT * 2.5 + State.CURVE_UNIT * 2))
        self.sensorList.append(Sensor(1, 4, State.STRAIGHT_UNIT * 1.5 + State.CURVE_UNIT * 2))

        # Station(id, name)
        self.stationList.append(Station(0, "A"))  # A駅を追加
        self.stationList.append(Station(1, "B"))  # B駅を追加

        # station.setTrack(trackId, sectionId, stationPosition)
        Station.getById(0).setTrack(1, 0, State.STRAIGHT_UNIT * 3)  # 駅0の1番線はSection0
        Station.getById(1).setTrack(1, 2, State.STRAIGHT_UNIT * 3)  # 駅1の1番線はsection2
        Station.getById(1).setTrack(2, 3, State.STRAIGHT_UNIT * 3)  # 駅1の2番線はsection3

        # Train(initialSection, initialPosition)
        self.trainList.append(Train(0, Station.getById(0).trackDict.get(1), State.STRAIGHT_UNIT * 3))  # 駅0の1番線に配置
