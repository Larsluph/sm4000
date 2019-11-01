class Motor:

    SPEED_MAX=100
    
    def __init__(self,name):
        self.__name = name
        self.__speed = 0
        self.__running = False
        
    def run(self, speed=10):
        self.__speed = speed
        self.__running = True
        # send a message to the control card
        print("{} started at speed {}".format(self.getName(),self.getSpeed()))
        
    def cut(self):
        self.__running = False
        # send a message to the control card
        print("{} is cut".format(self.getName()))

    def isRunning(self):
        return self.__running
    
    def changeSpeed(self, speed):
        if self.isRunning():        
            if (0 <= self.__speed + speed <= self.SPEED_MAX):
                self.__speed += speed
                # send a message to the control card
                print("{} is now running at speed {}".format(self.getName(),self.getSpeed()))

    def increaseSpeed(self, speed=10):
        self.changeSpeed(speed)

    def decreaseSpeed(self, speed=-10):
        self.changeSpeed(speed)
        
    def getName(self):
        return self.__name
    
    def getSpeed(self):
        return self.__speed

    def __str__(self):
        if self.running:
            return "Motor {} runs at speed {}".format(self.getName(),self.getSpeed())
        else:
            return "Motor {} is cut".format(self.getName())
