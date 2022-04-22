from operator import truediv
from Operation import *

operation = Operation()
operation.state.communication.setup(simulationMode=True)

def init():
    
    return

def loop():
    while True:
        operation.update()
        time.sleep(1)


if __name__ == "__main__":
    init()
    loop()
