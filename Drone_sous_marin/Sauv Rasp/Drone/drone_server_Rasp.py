#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import module_commande_server_Rasp
import module_i2c_server_Rasp
import module_MPU9250_server_Rasp

def main():
    module_commande = threading.Thread(None, module_commande_server_Rasp.main, None)
    module_i2c = threading.Thread(None, module_i2c_server_Rasp.main, None)
    module_MPU9250 = threading.Thread(None, module_MPU9250_server_Rasp.main, None)

    module_MPU9250.start()

##    module_i2c.start()
##    time.sleep(5)
##    module_commande.start()

if __name__ == '__main__':
    main()
