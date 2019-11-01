from Motor import Motor

class Drone:

    def __init__ (self):
        self.__motors = dict()
        self.__sensors = dict()

    def addMotor (self, m):
        assert (isinstance(m,Motor))
        self.__motors[m.getName()] = m

    def addSensor (self, s):
        self.__sensors.append(s)

    def getMotor (self, name):
        assert (name in self.__motors.keys())
        return self.__motors[name]

    def getMotors (self):
        return self.__motors.values()
    
    def getSensor (self, name):
        assert (name in self.__sensors.keys())
        return self.__sensors[name]
        
        
