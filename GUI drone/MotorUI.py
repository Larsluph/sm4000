import tkinter as tk

class MotorUI(tk.Frame):

    def __init__(self, parent, m):
        tk.Frame.__init__(self, parent)
        self.__motor = m
        self.__mSpeedName  = tk.Label(self,text=m.getName())
        self.__mSpeedLabel = tk.Label(self,text=m.getSpeed())
        self.__mSpeedPlus  = tk.Button(self,text="+")
        self.__mSpeedMinus = tk.Button(self,text="-")
        self.__mSpeedOnOff = tk.Button(self,text="on")
        self.__mSpeedName.pack()
        self.__mSpeedLabel.pack()
        self.__mSpeedPlus.pack()
        self.__mSpeedMinus.pack()
        self.__mSpeedOnOff.pack()
        
        self.__mSpeedPlus.bind("<1>",self.__increase)
        self.__mSpeedMinus.bind("<1>",self.__decrease)
        self.__mSpeedOnOff.bind("<1>",self.__run)

    def __run(self,event):
        if self.__motor.isRunning():
            self.__motor.cut()
            self.__mSpeedOnOff["text"]="on"
        else:
            self.__motor.run()
            self.__mSpeedOnOff["text"]="off"

    def __increase(self,event):
        self.__motor.increaseSpeed()
        self.__updateSpeed()

    def __decrease(self,event):
        self.__motor.decreaseSpeed()        
        self.__updateSpeed()

    def __updateSpeed(self):
        self.__mSpeedLabel["text"] = self.__motor.getSpeed()    
