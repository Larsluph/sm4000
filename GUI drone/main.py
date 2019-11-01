from Drone import Drone
from Motor import Motor
from DroneUI import DroneUI

if __name__ == "__main__":

    d = Drone()
    d.addMotor(Motor("left"))
    d.addMotor(Motor("top"))
    d.addMotor(Motor("right"))

    ui = DroneUI(d)
    ui.run()

