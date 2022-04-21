import time
import State
import SignalSystem
import ATS
import DiaController

state = State.State()
signalSystem = SignalSystem.SignalSystem(state)
ats = ATS.ATS(state, signalSystem, STOPMERGIN = 20.0)
diaController = DiaController.DiaController(state)


def init():
    state.communication.simulationMode = True
    state.communication.setup()
    return

def loop():
    while True:
        state.update()
        diaController.update()
        time.sleep(1)


if __name__ == "__main__":
    init()
    loop()
