import tkinter as tk
from MotorUI import MotorUI

class DroneUI:

    def __init__(self, d):
        self.__app = tk.Tk()
        self.__drone = d
        self.__motorUI = [None for i in range(0,4)]

        i = 1
        for m in d.getMotors():
            self.__motorUI[i] = MotorUI(self.__app,m)
            self.__motorUI[i].grid(row=1, column=i, pady=5, padx=5)
            i += 1
            
    def run(self):
        self.__app.mainloop()

        
