import time
import State
import Communication

state = State.State()
communication = Communication.Communication()


def init():
    communication.simulationMode = True
    communication.setup()

def loop():
    while True:
        communication.update()
        time.sleep(1)


if __name__ == "__main__":
    init()
    loop()
