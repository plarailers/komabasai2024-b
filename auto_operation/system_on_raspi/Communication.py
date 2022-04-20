import platform
import serial
import queue
from Components import Junction

# ESP32 や Arduino との通信をまとめる。
# シミュレーションモードを使うと接続が無くてもある程度動作確認できる。


class Communication:
    class TrainSignal:
        def __init__(self, trainId: int, delta: int):
            self.trainId = trainId
            self.delta = delta

    def __init__(self):
        self.simulationMode = False
        self.simulationSpeedMap: dict[int, int] = {}
        self.arduino = None
        self.esp32Map: dict[int, serial.Serial] = {}
        self.trainSignalBuffer = queue.Queue()
        self.sensorSignalBuffer = queue.Queue()

    def setup(self):
        osName = platform.system()
        isWindows = osName.startswith("Windows")
        if self.simulationMode:
            if isWindows:
                self.simulationSpeedMap[0] = 0
                self.simulationSpeedMap[1] = 0
                # self.arduino = serial.Serial("COM8", 9600)
            else:
                self.simulationSpeedMap[0] = 0
                self.simulationSpeedMap[1] = 0
                # self.arduino = serial.Serial("/dev/ttyS0", 9600)
        else:
            if isWindows:
                self.esp32Map[0] = serial.Serial("COM5", 115200)
                self.esp32Map[1] = serial.Serial("COM6", 115200)
                self.arduino = serial.Serial("COM8", 9600)
            else:
                self.esp32Map[0] = serial.Serial("/dev/cu.ESP32-ESP32SPP", 115200)
                self.esp32Map[1] = serial.Serial("/dev/cu.ESP32-ESP32Dr.", 115200)
                self.arduino = serial.Serial("/dev/ttyS0", 9600)
        self.update()

    def update(self):
        if (self.simulationMode):
            for key, value in self.simulationSpeedMap.items():
                trainId = key
                speed = value
                if (speed > 0):
                    self.trainSignalBuffer.put(Communication.TrainSignal(trainId, speed))

            if self.arduino != None:
                while self.arduino.in_waiting > 0:
                    self.sensorSignalBuffer.put(self.arduino.read())

        else:
            for key, value in self.esp32Map.items():
                trainId = key
                esp32 = value
                if esp32 != None:
                    while esp32.in_waiting > 0:
                        self.trainSignalBuffer.add(Communication.TrainSignal(trainId, esp32.read()))

            if self.arduino != None:
                while self.arduino.in_waiting > 0:
                    self.sensorSignalBuffer.put(self.arduino.read())

    def availableTrainSignal(self) -> int:
        return self.trainSignalBuffer.qsize()

    def receiveTrainSignal(self) -> TrainSignal:
        return self.trainSignalBuffer.get()

    def availableSensorSignal(self) -> int:
        return self.sensorSignalBuffer.qsize()

    def receiveSensorSignal(self) -> int:
        return self.sensorSignalBuffer.get()

    # 指定した車両にinputを送る
    def sendInput(self, trainId: int, input: int):
        if self.simulationMode:
            self.simulationSpeedMap[trainId] = input
        else:
            if self.esp32Map[trainId] != None:
                self.esp32Map[trainId].write(input.to_bytes(1))

    # 指定したポイントに切替命令を送る
    def sendToggle(self, junctionId: int, servoState: Junction.ServoState):
        if self.arduino != None:
            servoStateCode = 0
            if servoState == Junction.ServoState.NoServo:
                return
            elif servoState == Junction.ServoState.Straight:
                servoStateCode = 0
            elif servoState == Junction.ServoState.Curve:
                servoStateCode = 1
            else:
                return
            self.arduino.write(junctionId.to_bytes(1), servoStateCode.to_bytes(1))
